import os, sys
from PIL import Image
import numpy as np

def _root(p):
    d = os.path.dirname(os.path.abspath(p))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, 'pet_frames')):
            return d
        d = os.path.dirname(d)
    raise SystemExit('找不到 pet_frames')


D = _root(__file__)
OUT = os.path.join(D, 'pet_frames', 'mimo')
os.makedirs(OUT, exist_ok=True)

SIZE = 64
FIG_H = 56
# 锁死 bbox：以最先两张为准，所有动作图都用这个框裁，保证像素级对齐
BBOX = (143, 129, 497, 549)


def cut_magenta(im):
    a = np.array(im.convert('RGB')).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bg = (r > 165) & (b > 165) & (g < 125) & (np.abs(r - b) < 80)
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    return np.dstack([a.astype(np.uint8), alpha])


def premult_resize(rgba, size):
    arr = rgba.astype(np.float32)
    rgb, al = arr[:, :, :3], arr[:, :, 3:4] / 255.0
    pm = rgb * al
    pm_img = Image.fromarray(np.clip(pm, 0, 255).astype(np.uint8))
    a_img = Image.fromarray((al[:, :, 0] * 255).astype(np.uint8), 'L')
    pm_r = np.array(pm_img.resize(size, Image.BOX)).astype(np.float32)
    a_r = np.array(a_img.resize(size, Image.BOX)).astype(np.float32) / 255.0
    return pm_r / np.clip(a_r[:, :, None], 1e-3, 1.0), a_r


def kmeans(pixels, k=16, iters=24, seed=0):
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
    """把 rgb/alpha 贴到 dst 的 (x,y)，超出边界的部分自动裁掉（不报错）"""
    h, w = alpha.shape
    H, W = dst.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sx, sy = x0 - x, y0 - y
    dst[y0:y1, x0:x1, :3] = rgb[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]
    dst[y0:y1, x0:x1, 3] = alpha[sy:sy + (y1 - y0), sx:sx + (x1 - x0)]


def process(src, name):
    arr = cut_magenta(Image.open(src))

    # 缩放比以「角色主体」（固定 BBOX）为准，符号之类的附加物不会把人挤小
    scale = FIG_H / float(BBOX[3] - BBOX[1])

    # 真实前景（含头顶的生气符号），向左上/右下扩出去，只扩不缩
    ys, xs = np.where(arr[:, :, 3] > 0)
    fx0, fy0, fx1, fy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    cx0, cy0 = min(BBOX[0], fx0), min(BBOX[1], fy0)
    cx1, cy1 = max(BBOX[2], fx1), max(BBOX[3], fy1)
    crop = arr[cy0:cy1, cx0:cx1]

    tw = max(1, round((cx1 - cx0) * scale))
    th = max(1, round((cy1 - cy0) * scale))
    rgb, al = premult_resize(crop, (tw, th))
    al = (al > 0.45).astype(np.uint8) * 255

    # 角色主体居中贴底；符号按它在裁剪区里的相对位置自然偏移
    base_x = (SIZE - round((BBOX[2] - BBOX[0]) * scale)) // 2
    base_y = SIZE - FIG_H
    px = base_x - round((BBOX[0] - cx0) * scale)
    py = base_y - round((BBOX[1] - cy0) * scale)

    # 大画布贴上去再裁，超出边界的部分（离得太远的符号）自然被裁掉
    big = np.zeros((SIZE * 3, SIZE * 3, 4), np.uint8)
    paste(big, np.clip(rgb, 0, 255).astype(np.uint8), al, SIZE + px, SIZE + py)
    canvas = big[SIZE:SIZE * 2, SIZE:SIZE * 2].copy()

    mask = canvas[:, :, 3] > 0
    px = canvas[mask][:, :3].astype(np.float32)
    cent = kmeans(px, k=16)
    d = ((px[:, None, :] - cent[None, :, :]) ** 2).sum(2)
    canvas[mask, :3] = cent[d.argmin(1)].round().astype(np.uint8)

    r, g, b = canvas[:, :, 0].astype(int), canvas[:, :, 1].astype(int), canvas[:, :, 2].astype(int)
    magenta = (r > 140) & (b > 140) & (g < 110) & (np.abs(r - b) < 80)
    canvas[magenta, 3] = 0

    img = Image.fromarray(canvas, 'RGBA')
    img.save(os.path.join(OUT, name + '.png'))
    print('%-10s fig %dx%d  色数 %d  bbox %s' % (
        name, tw, FIG_H,
        len(set(map(tuple, canvas[canvas[:, :, 3] > 0][:, :3]))), img.getbbox()))
    return canvas


if __name__ == '__main__':
    src, name = sys.argv[1], sys.argv[2]
    process(src, name)
