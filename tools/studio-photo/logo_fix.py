"""Replace a mangled AI-rendered logo with the official SILVERSYD logo.

usage: python3 logo_fix.py in.png out.png x0 y0 x1 y1 [width_px] [angle_deg] [opacity]
  (x0,y0,x1,y1) = box covering the broken logo; new logo is centered in it.
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageChops

src, dst = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
width = int(sys.argv[7]) if len(sys.argv) > 7 else int((x1 - x0) * 0.9)
angle = float(sys.argv[8]) if len(sys.argv) > 8 else 0.0
opacity = float(sys.argv[9]) if len(sys.argv) > 9 else 0.92

im = Image.open(src).convert("RGB")

# 1) erase old logo: fill box with fabric sampled from just above it, then soften edges
pad = 6
box = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
bh = box[3] - box[1]
patch = im.crop((box[0], box[1] - bh - 4, box[2], box[1] - 4))
mask = Image.new("L", im.size, 0)
mask.paste(255, box)
mask = mask.filter(ImageFilter.GaussianBlur(4))
filled = im.copy()
filled.paste(patch, box[:2])
im = Image.composite(filled, im, mask)

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
