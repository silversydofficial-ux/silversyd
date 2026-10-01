"""홀터넥 상세페이지 이미지 가공 (누끼, 크롭, 합성).

SRC 폴더에 원본을 두고 실행하면 ../img/ 에 웹용 이미지가 나온다.
  - raw/S_SSSS_*.jpg   오르빗관 0913 착샷 (차콜, 1500px)
  - raw/H_SILVERSYD_*.jpg  서울제조허브 0921 제품컷 (6053x4035)
  - ghost/*.jpg        스타일룸 고스트샷
  - rb_S*.png          rembg(birefnet-portrait)로 뽑은 누끼
  - raw/G194.png       stage 임시컷 (힉스필드 기존 생성본, 교체 예정)

usage: python3 prep_images.py SRC
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "img"
OUT.mkdir(exist_ok=True)

BEIGE = (243, 242, 240)  # --soft


def load(p):
    return Image.open(SRC / p)


def rel(im, box):
    w, h = im.size
    return im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))


def fit_ratio(im, ratio, anchor_y=0.5):
    """가로/세로 비율(ratio=w/h)로 중앙 크롭."""
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio)
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio)
    y = int((h - nh) * anchor_y)
    return im.crop((0, y, w, y + nh))


def on_bg(rgba, color, ratio=None, pad=0.06, bottom=True):
    """누끼를 단색 배경에 올린다. bottom=True면 발/하단 컷이 바닥에 닿게."""
    w, h = rgba.size
    if ratio:
        H = int(h * (1 + pad))
        W = max(int(H * ratio), int(w * (1 + pad * 2)))
        H = max(H, int(W / ratio))
    else:
        W, H = int(w * (1 + pad * 2)), int(h * (1 + pad))
    bg = Image.new("RGB", (W, H), color)
    y = H - h if bottom else (H - h) // 2
    bg.paste(rgba, ((W - w) // 2, y), rgba)
    return bg


def save(im, name, maxw=1200, q=82):
    im = im.copy()
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    path = OUT / f"{name}.webp"
    im.save(path, "WEBP", quality=q, method=6)
    print(f"{name:10s} {im.size[0]}x{im.size[1]}  {path.stat().st_size // 1024}KB")


def tight(im, thr=235, m=20):
    a = np.asarray(im.convert("L"))
    ys, xs = np.where(a < thr)
    return im.crop((max(xs.min() - m, 0), max(ys.min() - m, 0),
                    min(xs.max() + m, im.width), min(ys.max() + m, im.height)))


def dark_bw(rgba, ratio=3 / 4, top=42, gamma=1.35):
    """누끼를 어두운 비네트 배경 + 흑백으로 합성 (블랙 반전 섹션용)."""
    m = rgba.split()[3]
    H = int(rgba.height * 1.08)
    W = int(H * ratio)
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.35) / H) ** 2)
    v = (top - 60 * d).clip(8, top).astype("uint8")
    bg = Image.fromarray(np.dstack([v] * 3))
    g = ImageOps.grayscale(rgba.convert("RGB"))
    g = Image.eval(g, lambda p: int(255 * ((p / 255) ** gamma)))
    bg.paste(Image.merge("RGB", [g] * 3), ((W - rgba.width) // 2, H - rgba.height), m)
    return bg


# ---- 모델컷 (실촬영 차콜) ----
hero = load("rb_S163.png")
save(hero, "hero", maxw=1000)  # 투명 누끼 그대로

save(fit_ratio(rel(tight(load("raw/S_SSSS_131.jpg").convert("RGB")), (0, 0.02, 1, 0.55)), 1.0), "front")
save(dark_bw(load("rb_S186.png")), "back")
save(fit_ratio(tight(load("raw/S_SSSS_142.jpg").convert("RGB")), 3 / 4, 0.0), "side")
save(on_bg(load("rb_S167.png"), (255, 255, 255), ratio=3 / 4, pad=0.04), "full")
save(fit_ratio(rel(tight(load("raw/S_SSSS_150.jpg").convert("RGB")), (0.05, 0.12, 0.95, 0.70)), 3 / 4, 0.2), "detail")

for k, n in (("cut1", 164), ("cut2", 183), ("cut3", 187)):
    save(load(f"rb_S{n}.png"), k, maxw=800)

# LOOK 콜라주 01~05: 누끼를 중간톤 배경에 올려 흰 번호가 읽히게
for i, n in enumerate((170, 135, 181, 190, 129), 1):
    save(on_bg(load(f"rb_S{n}.png"), (178, 174, 168), ratio=3 / 4), f"look{i}", maxw=900)

# ---- 제품 ----
save(load("ghost/131365.jpg").convert("RGB"), "ghost", maxw=1000)
for k, f in (("col_black", "131365"), ("col_charcoal", "131359"),
             ("col_burgundy", "131366"), ("col_blue", "131367")):
    save(fit_ratio(load(f"ghost/{f}.jpg").convert("RGB"), 3 / 4), k, maxw=800)

# 원단 매크로 (컬러 4분할 배경) 3:4
for k, f, box in (("fab0", "H_SILVERSYD_82", (0.62, 0.35, 0.80, 0.75)),
                  ("fab1", "H_SILVERSYD_72", (0.12, 0.42, 0.38, 0.95)),
                  ("fab2", "H_SILVERSYD_100", (0.43, 0.55, 0.57, 0.92)),
                  ("fab3", "H_SILVERSYD_52", (0.10, 0.45, 0.35, 0.95))):
    save(fit_ratio(rel(load(f"raw/{f}.jpg").convert("RGB"), box), 3 / 4), k, maxw=900)

# 클로즈업 매크로 4:3 (스트랩, 패드, 밴딩)
for k, f, box in (("z1", "H_SILVERSYD_82", (0.10, 0.28, 0.40, 0.62)),
                  ("z2", "H_SILVERSYD_75", (0.30, 0.12, 0.67, 0.55)),
                  ("z3", "H_SILVERSYD_83", (0.38, 0.20, 0.78, 0.65))):
    save(fit_ratio(rel(load(f"raw/{f}.jpg").convert("RGB"), box), 4 / 3), k, maxw=1200)

# ---- stage: 임시 (힉스필드 기존 생성본 G194를 21:9로). 생성 후 교체 ----
st = load("raw/G194.png").convert("RGB")
save(fit_ratio(st, 21 / 9, 0.25), "stage", maxw=1600)
save(ImageOps.grayscale(fit_ratio(st, 4 / 5, 0.2)).convert("RGB"), "brand", maxw=1200)

# ---- 시리즈/셋업 카드 ----
save(fit_ratio(load("ghost/fix_131012.jpg").convert("RGB"), 3 / 4), "shorts", maxw=800)
top = load("ghost/131365.jpg").convert("RGB")
bot = load("ghost/fix_131012.jpg").convert("RGB")
s = 900
canvas = Image.new("RGB", (s, int(s * 4 / 3)), (255, 255, 255))
t = tight(top, 245); t.thumbnail((int(s * 0.62), int(s * 0.7)))
b = tight(bot, 245); b.thumbnail((int(s * 0.56), int(s * 0.5)))
canvas.paste(t, ((s - t.width) // 2, 60))
canvas.paste(b, ((s - b.width) // 2, 60 + t.height + 24))
save(canvas, "set", maxw=900)
