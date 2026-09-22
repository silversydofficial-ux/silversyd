#!/usr/bin/env python3
"""
SILVERSYD 상품 상세컷 배경 톤 매칭 도구.

ai-model-guide.md 의 "상품 상세컷 고정 배경 규칙"(2026-09-14 확정)에 맞춰
이미 생성된 스튜디오 컷의 배경 톤만 보정한다.

핵심: 인물/제품 픽셀은 건드리지 않는다. 배경 마스크를 만든 뒤 배경 픽셀에만
채널별 평균·표준편차를 기준값에 정렬시키므로
  - 웜/블루 틴트가 제거되고 (R=G=B)
  - 명도가 기준과 맞춰지며
  - 바닥 그라데이션과 접지 그림자의 구조는 그대로 남는다.

사용법:
    python3 bg_match.py --check  <이미지|URL> ...       # 측정만, 파일 안 씀
    python3 bg_match.py --outdir out  <이미지|URL> ...  # 보정본 생성
    python3 bg_match.py --ref 기준.png <이미지> ...     # 기준 샘플 직접 지정

의존성: pillow, numpy, scipy
"""
import argparse
import os
import sys
import tempfile
import urllib.request

import numpy as np
from PIL import Image
from scipy import ndimage

# ai-model-guide.md 의 "톤 비교 기준 샘플"을 이 스크립트의 마스크 기준으로 측정한 값.
# --ref 로 기준 이미지를 주면 이 값 대신 실측값을 쓴다.
DEFAULT_TARGET_MEAN = 220.7
DEFAULT_TARGET_STD = 18.2

# 합격 기준
TINT_TOLERANCE = 2.0    # |R-B|
MEAN_TOLERANCE = 4.0    # 기준 평균과의 차이


def load(path):
    """로컬 경로 또는 https URL 을 RGB 배열로 읽는다."""
    if path.startswith(("http://", "https://")):
        suffix = os.path.splitext(path)[1] or ".png"
        fd, tmp = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        urllib.request.urlretrieve(path, tmp)
        path = tmp
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float32)


def bg_mask(a):
    """배경 소프트 마스크를 만든다. 1 = 배경, 0 = 피사체.

    저채도 + 충분히 밝음 + 테두리와 연결됨 = 배경으로 본다.
    피사체 내부의 밝은 영역(흰 신발, 로고 등)은 테두리와 끊겨 있으므로 제외된다.
    """
    h, w, _ = a.shape
    sat = a.max(2) - a.min(2)
    lum = a.mean(2)

    ph, pw = h // 14, w // 14
    seed_lum = np.concatenate([a[:ph, :pw].reshape(-1, 3),
                               a[:ph, -pw:].reshape(-1, 3)]).mean()

    cand = (sat < 26) & (lum > seed_lum - 95)
    lab, _ = ndimage.label(cand)
    border = set(np.unique(np.concatenate([lab[0, :], lab[-1, :],
                                           lab[:, 0], lab[:, -1]])))
    border.discard(0)
    m = np.isin(lab, list(border))

    subj = ndimage.binary_fill_holes(~m)                    # 피사체를 꽉 채운다
    subj = ndimage.binary_dilation(subj, np.ones((5, 5)))   # 소프트 엣지 여유
    return np.clip(ndimage.gaussian_filter((~subj).astype(np.float32), 3.0), 0, 1)


def measure(a, mask=None):
    """배경 영역의 평균 RGB / 표준편차 / 틴트(R-B) / 마스크 커버리지."""
    m = bg_mask(a) if mask is None else mask
    sel = m > 0.9
    if sel.sum() < 100:
        return None
    # float64 로 누적한다. float32 로 채널축(비연속 스트라이드) 평균을 내면
    # 수백만 픽셀에서 누적 오차가 수 단위로 쌓여 틴트 판정이 틀어진다.
    px = a[sel].astype(np.float64)
    mean = px.mean(0)
    return {"mean": mean, "lum": px.mean(), "std": px.std(),
            "tint": float(mean[0] - mean[2]), "coverage": float(m.mean())}


def correct(a, mask, target_mean, target_std):
    """배경 픽셀만 채널별로 기준 평균·표준편차에 정렬시킨다."""
    sel = mask > 0.9
    out = a.copy()
    for c in range(3):
        ch = a[:, :, c]
        px = ch[sel].astype(np.float64)
        mu = px.mean()
        sd = max(float(px.std()), 1e-3)
        # 게인을 제한해 배경 그라데이션 구조가 과도하게 눌리거나 벌어지지 않게 한다
        gain = float(np.clip(target_std / sd, 0.6, 1.6))
        out[:, :, c] = (ch - mu) * gain + target_mean
    m3 = mask[:, :, None]
    return np.clip(a * (1 - m3) + out * m3, 0, 255)


def verdict(stats, target_mean):
    if stats is None:
        return "SKIP (배경 마스크 검출 실패)"
    ok_tint = abs(stats["tint"]) <= TINT_TOLERANCE
    ok_mean = abs(stats["lum"] - target_mean) <= MEAN_TOLERANCE
    if ok_tint and ok_mean:
        return "PASS"
    reasons = []
    if not ok_tint:
        reasons.append("틴트" if stats["tint"] > 0 else "블루틴트")
    if not ok_mean:
        reasons.append("밝음" if stats["lum"] > target_mean else "어두움")
    return "FAIL (" + ", ".join(reasons) + ")"


def fmt(stats):
    if stats is None:
        return "-"
    m = stats["mean"]
    return f"({m[0]:5.1f},{m[1]:5.1f},{m[2]:5.1f}) R-B={stats['tint']:+5.1f}"


def main():
    p = argparse.ArgumentParser(description="SILVERSYD 상세컷 배경 톤 매칭")
    p.add_argument("images", nargs="+", help="로컬 경로 또는 https URL")
    p.add_argument("--ref", help="기준 샘플 이미지. 주면 타겟값을 실측한다")
    p.add_argument("--check", action="store_true", help="측정만 하고 파일을 쓰지 않는다")
    p.add_argument("--outdir", default="bg_fixed", help="보정본 출력 폴더")
    p.add_argument("--suffix", default="_bgfix", help="출력 파일명 접미사")
    args = p.parse_args()

    target_mean, target_std = DEFAULT_TARGET_MEAN, DEFAULT_TARGET_STD
    if args.ref:
        ref_stats = measure(load(args.ref))
        if ref_stats is None:
            sys.exit("기준 샘플에서 배경을 찾지 못했습니다.")
        target_mean, target_std = ref_stats["lum"], ref_stats["std"]
    print(f"타겟: 평균 {target_mean:.1f} / 표준편차 {target_std:.1f} "
          f"/ 허용 |R-B| <= {TINT_TOLERANCE} / 평균 오차 <= {MEAN_TOLERANCE}\n")

    if not args.check:
        os.makedirs(args.outdir, exist_ok=True)

    for src in args.images:
        name = os.path.basename(src.split("?")[0])
        try:
            a = load(src)
        except Exception as exc:                      # 네트워크/포맷 오류는 건너뛴다
            print(f"{name:44} 읽기 실패: {exc}")
            continue

        mask = bg_mask(a)
        before = measure(a, mask)
        if before is None:
            print(f"{name:44} {verdict(before, target_mean)}")
            continue

        line = f"{name:44} bg{before['coverage']*100:5.1f}%  전 {fmt(before)}  {verdict(before, target_mean)}"
        if args.check:
            print(line)
            continue

        fixed = correct(a, mask, target_mean, target_std)
        after = measure(fixed, mask)
        stem, ext = os.path.splitext(name)
        dst = os.path.join(args.outdir, f"{stem}{args.suffix}{ext or '.png'}")
        Image.fromarray(fixed.astype(np.uint8)).save(dst)
        print(f"{line}\n{'':44}          후 {fmt(after)}  {verdict(after, target_mean)}  -> {dst}")


if __name__ == "__main__":
    main()
