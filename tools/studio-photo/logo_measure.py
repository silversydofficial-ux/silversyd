"""Measure logo width as % of torso width on a dark garment.

usage: python3 logo_measure.py image.png x0 y0 x1 y1
  (x0,y0,x1,y1) = box tightly around the logo, fully inside the fabric (no backdrop).
Reference: SYD-tee-black-v5 ghost shot = 17.1%.
"""
import sys
import numpy as np
from PIL import Image

REF = 17.1
path = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2:6])
g = np.asarray(Image.open(path).convert("L")).astype(int)
ys, xs = np.where(g[y0:y1, x0:x1] > 150)
ys += y0
xs += x0
row = (ys.min() + ys.max()) // 2
line = g[row]
l = xs.min() - 3
while l > 0 and line[l - 1] < 150:
    l -= 1
r = xs.max() + 3
while r < len(line) - 1 and line[r + 1] < 150:
    r += 1
lw, tw = xs.max() - xs.min() + 1, r - l
pct = lw / tw * 100
print(f"logo x{xs.min()}-{xs.max()} y{ys.min()}-{ys.max()} w={lw}px | torso x{l}-{r} w={tw}px")
print(f"logo/torso = {pct:.1f}% (ref {REF}%) -> {pct / REF * 100:.0f}% of reference")
print(f"target logo width for {REF}%: {round(tw * REF / 100)}px")
