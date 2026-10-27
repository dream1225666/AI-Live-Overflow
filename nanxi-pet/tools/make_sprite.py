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


def process(src, name):
    arr = cut_magenta(Image.open(src))
    x0, y0, x1, y1 = BBOX
    crop = arr[y0:y1, x0:x1]

    h, w = crop.shape[:2]
    tw = max(1, round(w * FIG_H / h))
    rgb, al = premult_resize(crop, (tw, FIG_H))
    al = (al > 0.45).astype(np.uint8) * 255

    canvas = np.zeros((SIZE, SIZE, 4), np.uint8)
    ox, oy = (SIZE - tw) // 2, SIZE - FIG_H
    canvas[oy:oy + FIG_H, ox:ox + tw, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    canvas[oy:oy + FIG_H, ox:ox + tw, 3] = al

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
