import os
import sys

from PIL import Image, ImageFilter
import numpy as np

SIZE = 64
FIG_H = 56
BASE_W = 640
BBOX_640 = (143, 129, 497, 549)


def root_dir(p):
    d = os.path.dirname(os.path.abspath(p))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, 'pet_frames')):
            return d
        d = os.path.dirname(d)
    raise SystemExit('找不到 pet_frames')


D = root_dir(__file__)
OUT = os.path.join(D, 'pet_frames', 'mimo')
os.makedirs(OUT, exist_ok=True)


def bbox_for(w):
    s = w / float(BASE_W)
    return tuple(int(round(v * s)) for v in BBOX_640)


def cut_magenta(im):
    """抠品红。判定放宽到含边缘混色，再做 1px 腐蚀，粉边一次清干净。"""
    rgb = np.array(im.convert('RGB'))
    a = rgb.astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bg = (r > 150) & (b > 140) & (g < 150) & ((r - g) > 45) & ((b - g) > 35)
    al = np.where(bg, 0, 255).astype(np.uint8)
    al = np.array(Image.fromarray(al).filter(ImageFilter.MinFilter(3)))
    # 块内中值滤波：去掉伪像素块里的噪点，缩小后不会糊成灰
    rgb = np.array(Image.fromarray(rgb).filter(ImageFilter.MedianFilter(5)))
    return rgb, al


def kmeans(pixels, k=24, iters=30, seed=0):
    rs = np.random.RandomState(seed)
    cent = pixels[rs.choice(len(pixels), min(k, len(pixels)), replace=False)].copy()
    for _ in range(iters):
        d = ((pixels[:, None, :] - cent[None, :, :]) ** 2).sum(2)
        lab = d.argmin(1)
        for j in range(len(cent)):
            m = lab == j
            if m.any():
                cent[j] = pixels[m].mean(0)
    return cent


def paste(dst, rgb, alpha, x, y):
    h, w = alpha.shape
    H, W = dst.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sx, sy = x0 - x, y0 - y
    dst[y0:y1, x0:x1, :3] = rgb[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
    dst[y0:y1, x0:x1, 3] = alpha[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]


def process(src, name, save=True):
    im = Image.open(src)
    rgb, al = cut_magenta(im)
    BB = bbox_for(im.size[0])
    scale = FIG_H / float(BB[3] - BB[1])

    ys, xs = np.where(al > 0)
    fx0, fy0, fx1, fy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    cx0, cy0 = min(BB[0], fx0), min(BB[1], fy0)
    cx1, cy1 = max(BB[2], fx1), max(BB[3], fy1)

    crop_rgb = rgb[cy0:cy1, cx0:cx1]
    crop_al = al[cy0:cy1, cx0:cx1]
    tw = max(1, round((cx1 - cx0) * scale))
    th = max(1, round((cy1 - cy0) * scale))

    # NEAREST：直接取原生像素点，不做颜色平均，黑发不会被混成灰
    r_small = np.array(Image.fromarray(crop_rgb).resize((tw, th), Image.NEAREST))
    a_small = np.array(Image.fromarray(crop_al).resize((tw, th), Image.NEAREST))
    a_small = np.where(a_small > 127, 255, 0).astype(np.uint8)

    base_x = (SIZE - round((BB[2] - BB[0]) * scale)) // 2
    base_y = SIZE - FIG_H

    big = np.zeros((SIZE * 3, SIZE * 3, 4), np.uint8)
    paste(big, r_small, a_small,
          SIZE + base_x - round((BB[0] - cx0) * scale),
          SIZE + base_y - round((BB[1] - cy0) * scale))
    canvas = big[SIZE:SIZE * 2, SIZE:SIZE * 2].copy()

    mask = canvas[:, :, 3] > 0
    if mask.any():
        px = canvas[mask][:, :3].astype(np.float32)
        cent = kmeans(px, k=24)
        d = ((px[:, None, :] - cent[None, :, :]) ** 2).sum(2)
        canvas[mask, :3] = cent[d.argmin(1)].round().astype(np.uint8)

    # 缩放后仍残留的品红像素直接砍掉
    rr, gg, bb = (canvas[:, :, 0].astype(int), canvas[:, :, 1].astype(int),
                  canvas[:, :, 2].astype(int))
    mag = (rr > 150) & (bb > 140) & ((rr - gg) > 45) & ((bb - gg) > 35)
    left = (mag & (canvas[:, :, 3] > 0)).sum()
    canvas[mag, 3] = 0

    if save:
        Image.fromarray(canvas, 'RGBA').save(os.path.join(OUT, name + '.png'))
        cols = len(set(map(tuple, canvas[canvas[:, :, 3] > 0][:, :3])))
        print('%-12s %dx%d 色数 %d 清掉品红 %d' % (name, tw, th, cols, left))
    return canvas


if __name__ == '__main__':
    process(sys.argv[1], sys.argv[2])
