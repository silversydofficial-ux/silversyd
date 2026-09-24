"""Replace a mangled AI-rendered logo with the official SILVERSYD logo.

usage: python3 logo_fix.py in.png out.png x0 y0 x1 y1 [width_px] [angle_deg] [opacity]
  (x0,y0,x1,y1) = box covering the broken logo; new logo is centered in it.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
width = int(sys.argv[7]) if len(sys.argv) > 7 else int((x1 - x0) * 0.9)
angle = float(sys.argv[8]) if len(sys.argv) > 8 else 0.0
opacity = float(sys.argv[9]) if len(sys.argv) > 9 else 0.92

im = Image.open(src).convert("RGB")

# 1) erase old logo: mask only the bright print pixels inside the box and fill them from
#    the surrounding fabric (normalized blur), so no rectangular patch edge is left
pad = 6
bx0, by0, bx1, by1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
arr = np.asarray(im).astype(np.float32)
reg = arr[by0 - 20:by1 + 20, bx0 - 20:bx1 + 20]
lum = reg.mean(axis=2)
hole = np.zeros(lum.shape, bool)
hole[20:-20, 20:-20] = lum[20:-20, 20:-20] > 60
hole = np.asarray(Image.fromarray(hole.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
known = (~hole).astype(np.float32)
filled = reg.copy()
for r in (3, 6, 12):
    num = np.stack([np.asarray(Image.fromarray(np.clip(reg[..., c] * known, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) for c in range(3)], axis=2)
    den = np.asarray(Image.fromarray((known * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)[..., None] / 255
    est = num / np.maximum(den, 1e-3)
    todo = hole & (den[..., 0] > 0.05)
    filled[todo] = est[todo]
    known = np.maximum(known, todo.astype(np.float32))
    hole = hole & ~todo
arr[by0 - 20:by1 + 20, bx0 - 20:bx1 + 20] = filled
im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

# 2) official logo, white, scaled + rotated
logo = Image.open(Path(__file__).resolve().parents[2] / "assets/logo/silversyd-logo@3x-1200w.png").convert("RGBA")
alpha = logo.split()[3]
h = round(logo.height * width / logo.width)
alpha = alpha.resize((width, h), Image.LANCZOS)
if angle:
    alpha = alpha.rotate(angle, resample=Image.BICUBIC, expand=True)
alpha = alpha.filter(ImageFilter.GaussianBlur(0.35))  # print softness at this scale

# 3) modulate by fabric shading so the print sits on the fabric, not above it
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
ox, oy = cx - alpha.width // 2, cy - alpha.height // 2
region = im.crop((ox, oy, ox + alpha.width, oy + alpha.height)).convert("L")
shade = region.point(lambda v: int(205 + min(v, 60)))  # darker folds -> slightly dimmer ink
ink = Image.merge("RGB", (shade, shade, shade))
a = alpha.point(lambda v: int(v * opacity))
im.paste(ink, (ox, oy), a)
im.save(dst)
print("logo placed at", ox, oy, alpha.size)
