# 스튜디오 상세컷 후보정 도구 (힉스필드)

힉스필드로 만든 상품 착용 스튜디오컷을 로고·배경 기준에 맞추는 스크립트 모음.
필요 패키지: `pip install pillow numpy`

## 확정 프로세스

1. **생성** — 새로 생성 (기존 이미지 편집은 얼굴·바지·로고까지 같이 바뀌어서 쓰지 않음)
   - 프롬프트에 모델·의상 엘리먼트 `<<<element_id>>>` 삽입
   - `medias`에 포즈 레퍼런스 + 소품 레퍼런스 + **공식 로고 이미지**(흰 로고/검정 배경) 첨부
     → 엘리먼트 고스트샷의 로고는 이미지 폭의 ~3%라 철자가 뭉개짐. 큰 공식 로고를 같이 넣어야 SILVERSYD 철자가 정확히 나옴
2. **로고 실측** — `logo_measure.py`로 로고 폭 ÷ 몸통 폭 측정 (눈대중 금지)
3. **로고 교체(필요 시)** — 철자가 뭉개졌거나 크기가 기준 ±10%를 벗어나면 `logo_fix.py`로 공식 로고 파일로 교체
4. **배경 보정** — 힉스필드 `remove_background`로 누끼 → `bg_fix.py`로 배경만 #F7F7F7 무채색으로 맞춤
   (프롬프트로는 #C0~#E0 사이로 매번 흔들려서 후보정이 필수)

## 스크립트

| 파일 | 용도 |
|---|---|
| `logo_measure.py image.png x0 y0 x1 y1` | 로고를 감싸는 박스(원단 안쪽만)를 주면 로고 폭/몸통 폭 %와 기준 대비 %, 목표 픽셀 폭 출력 |
| `logo_fix.py in.png out.png x0 y0 x1 y1 [폭px] [각도] [불투명도]` | 박스 안의 기존 로고를 원단으로 덮고 `assets/logo/silversyd-logo@3x-1200w.png`를 흰색으로 올림. 원단 음영을 반영해 프린트처럼 보이게 함 |
| `bg_fix.py 원본.png 누끼.png out.png [247] [0.3]` | 누끼 알파를 마스크로 배경만 중앙값 #F7F7F7(R=G=B)로 재톤. 그림자 깊이 유지, 머리카락 경계 색번짐 제거 |

## 로고 크기 기준 (고스트샷 실측)

| 품목 | 로고 폭 ÷ 몸통 폭 |
|---|---|
| 텐션핏 티셔츠 (`SYD-tee-*-v5`) | **17.1%** (블랙 고스트샷 실측) |
| 홀터 탑 (`SYD-halter-*-v5`) | 약 12% (엘리먼트 설명 기준, 미실측) |
| 3부 쇼츠 (`SYD-shorts-*-v5`) | 약 16% (힙 폭 기준, 엘리먼트 설명 기준, 미실측) |

## 프롬프트 메모

- 배경: `bright, almost white, true neutral light grey seamless paper studio backdrop #F7F7F7, R=G=B, no tint ...`
  — `cool-toned`, `radial gradient` 금지 (브랜드 가이드 2026-09-14 규칙)
- 티셔츠 핏: `two sizes smaller ... second-skin compression fit like a rash guard`, 소매는 `sleeve hem grips the upper arm with ZERO gap`
- 원단: `thick dense high-polyester athletic knit like swimwear fabric, fully opaque, completely matte, not cotton`
- 로고: `reproduce the logo EXACTLY as in the logo reference image ... side by side in ONE horizontal line ... about 15% of torso width`
  (15%로 요청하면 실제 결과가 17% 전후로 나옴)
- 모델은 Nano Banana Pro로 요청해도 힉스필드에서 Nano Banana 2로 처리되는 경우가 있음
