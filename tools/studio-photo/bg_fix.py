"""Re-tone a studio backdrop to neutral #F7F7F7 while keeping the subject, floor shadow and hair edges.

usage: python3 bg_fix.py original.png cutout.png out.png [target=247] [gamma=0.3] [erode=3]
  cutout.png = same image with transparent background (alpha = subject mask)
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, cut, dst = sys.argv[1:4]
target = float(sys.argv[4]) if len(sys.argv) > 4 else 247.0
gamma = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3
erode = int(sys.argv[6]) if len(sys.argv) > 6 else 3  # odd px; raise to 5 if a light halo shows

img = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
mask_img = Image.open(cut).convert("RGBA").split()[3].resize(Image.open(src).size, Image.LANCZOS)
a = np.asarray(mask_img.filter(ImageFilter.MinFilter(erode)).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32)[..., None] / 255.0

# old backdrop: luminance, smoothed, with the subject region filled from surrounding backdrop
lum = img.mean(axis=2)
bg_only = a[..., 0] < 0.02
ref = np.median(lum[bg_only])
# fill subject area with a blurred estimate of the backdrop so edges can be de-contaminated
fill = Image.fromarray(np.where(bg_only, lum, ref).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))
old_bg_lum = np.where(bg_only, lum, np.asarray(fill).astype(np.float32))
old_bg = np.where(bg_only[..., None], img, old_bg_lum[..., None])

# new backdrop: neutral grey, same relative light falloff/shadow, compressed toward target
rel = np.clip(old_bg_lum / ref, 0.2, 1.6)
# compress bright falloff, keep shadows (rel<1) closer to their original depth
new_lum = np.clip(target * np.where(rel < 1, rel ** 0.9, rel ** gamma), 0, 255)
new_bg = np.repeat(new_lum[..., None], 3, axis=2)

# de-contaminate edge pixels (hair etc.): F = (I - (1-a)B_old) / a, then recomposite on B_new
safe_a = np.clip(a, 0.05, 1.0)
fg = np.clip((img - (1 - a) * old_bg) / safe_a, 0, 255)
fg = np.where(a > 0.05, fg, img)
out = a * fg + (1 - a) * new_bg
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst)
print(f"backdrop median {ref:.1f} -> {target}")
