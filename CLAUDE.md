# 실버시드 작업 규칙

- 실버시드(silversyd.com) 또는 카페24 스킨 작업은 **`silversyd-cafe24` 스킬을 먼저 로드하고 그 흐름(재현, 원인 특정, 새 블록 작성, 금지 문자 검사, 라이브 주입 검증, 가이드 전달, 적용 확인)을 따른다.** 브랜드 톤은 `silversyd-brand` 스킬을 함께 참고한다.
- 스킬 원본: `.claude/skills/silversyd-cafe24/` (사용자 계정용 사본은 `~/.claude/skills/silversyd-cafe24/`).
- 이 저장소의 `skin/` 은 참고용 사본이다. 라이브 기준 사실은 `scripts/list_blocks.py`, `scripts/live_check.py` 로 다시 확인한다.
- 산출물과 보고에 가로 대시(—)와 중간점(·)을 쓰지 않는다.

## 검증 도구 (클라우드 세션)

미리 설치된 Chromium(1194)에 맞춰 playwright 버전을 고정한다. 최신 버전은 브라우저를 못 찾는다.

    pip3 install "playwright==1.56.0"
    python3 -m playwright install webkit && python3 -m playwright install-deps webkit
