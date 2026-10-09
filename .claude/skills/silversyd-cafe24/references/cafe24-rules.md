# 카페24 스마트디자인 작업 규칙

실버시드에서 정립했고 다른 카페24 쇼핑몰에도 그대로 쓸 수 있다.

## 1. 편집기가 코드를 바꿔 버림 (가장 중요)

카페24 디자인 편집기는 저장할 때 코드를 조용히 변조한다. 콘솔 오류도 안 나서 원인 찾기가 어렵다.

- `$$` 가 `$` 로 줄어든다. 그래서 **jQuery 스타일 `$` 헬퍼 금지.** `q`, `qa` 같은 이름을 쓴다.
- 정규식 안의 태그 글자(`<br\s*\/?>` 의 `>`)가 `&gt;` 로 바뀐다. **정규식에 태그 글자를 쓰지 말고 DOM 조작으로 대체.**
- 정규식 끝의 단일 `$`(`/...$/`)는 안 바뀐다. 문제는 `$$` 와 `?>` 계열. 그래도 안전하게 `$` 는 아예 쓰지 않는다.
- `</head`, `</body` 리터럴을 쓰면 카페24가 그 자리에 자기 코드를 끼워 넣어 파일이 두 동강 난다.
- `http` 가 들어간 주소는 편집기와 채팅에서 자동 링크로 깨지기 쉽다. `//도메인/경로` 프로토콜 상대 주소를 작은따옴표 문자열에 담는다.
- **전달 전 `scripts/check_forbidden.py` 로 0 확인.** 손으로 할 때는 `grep -oF` 고정문자열 검색(`grep -c '$'` 는 모든 줄이 걸림).
- 스마트디자인 변수 `{$mall_name}` 같은 `$` 는 카페24 문법이므로 사용자가 관리자 화면(약관 등)에 붙이는 텍스트에는 있을 수 있다. 우리 코드에는 쓰지 않는다.

## 2. 코드 전달 방식

- **복사 버튼이 달린 단독 HTML 페이지로 준다** (`scripts/make_guide.py`). 마크다운이나 채팅으로 주면 URL 이 `<https://...>` 로 자동 링크되어 이미지가 깨지고 문법 오류가 난다.
- **편집기 검색은 여러 줄을 못 찾고, 역슬래시, 괄호, 대괄호, 들여쓰기가 섞인 줄도 못 찾는다.** 찾기 값은 특수문자 없는 한 줄짜리 평범한 앵커로. 주석 한 줄이 가장 안전하다. (실제 사고: `getCards([` 앵커를 줬다가 검색 0건)
- 기존 블록을 지우지 않고 **마지막 블록의 끝 주석 뒤에 새 블록을 덧붙이는** 방식이 안전하다. 롤백은 그 블록만 지우면 된다. 바꿀 내용 칸에는 찾은 앵커 줄을 맨 위에 그대로 다시 넣는다.
- 옛 블록을 비활성화할 때는 삭제 대신 `<template>` 으로 감싼다(시작 주석 뒤에 `<template>`, 끝 주석 앞에 `</template>`). 방문자가 계속 내려받으므로 정리 시점에 제거한다.
- 블록마다 `<!-- SILVERSYD 이름 시작 -->` / `<!-- SILVERSYD 이름 끝 -->` 주석. 상세설명 CSS 는 `<!-- BRAND 상세설명 ... 시작/끝 -->`.
- 같은 블록에 CSS 패치를 여러 번 할 때는 **누적 합본**으로 만들어, 이전 패치 적용 여부와 무관하게 한 번만 붙이면 되게 한다.
- 사용자는 찾기/바꾸기 방식을 선호한다. 한 파일에 단계별 안내와 복사 버튼, 되돌리는 법, 확인한 내용을 같이 둔다.

## 3. 스킨 파일 접근과 적용 위치

- 관리자 로그인 없이 공개 주소로 스킨 파일을 볼 수 있다: `https://도메인/layout/basic/css/<이름>.css`, `/layout/basic/js/layout.js`, `/js/common.js`. 경로 앞에 스킨 폴더명을 붙이면 404. 확인할 때는 `?v=타임스탬프` 를 붙인다.
- CSS/JS 번들은 `/ind-script/optimizer.php`, `optimizer_user.php`. 링크의 `filename=` 을 urldecode, urlsafe base64 디코드, `zlib.decompress(b, -15)` 하면 파일 경로가 순서대로 나온다(`scripts/decode_optimizer.py`).
- 카페24는 head 와 body 의 `@css` 를 모두 head 끝 optimizer 링크 하나로 모은다. 따라서 **head 인라인 style 은 스킨 CSS 보다 먼저, body 인라인 style 은 나중에** 적용된다. 스킨을 이기려면 body 쪽에 넣는다. (실제 사례: head 에 넣은 태블릿 핫픽스가 무효, body 끝으로 옮기니 해결)
- JS optimizer 는 body 맨 끝(인라인 스크립트보다 뒤)에 온다. 스킨 JS 가 만든 요소를 다루려면 DOMContentLoaded 이후 또는 MutationObserver.
- 선택자가 스킨과 글자 단위로 같으면 명시도가 같아 **나중에 로드된 쪽이 이긴다.** `!important` 끼리 부딪히면 명시도를 한 단계 올린다(`#header#header`, 클래스 반복 `.a.a`, `html:not(.x) .y`).
- 주문서/주문완료 페이지는 **별도 레이아웃**이라 layout.html 블록이 하나도 안 들어간다. 그 페이지 HTML 파일 맨 위/아래에 따로 붙인다. 로그인, 약관동의, 회원가입(member/login.html, agreement.html, join.html)도 각 파일 맨 아래에 붙였다.

## 4. 라이브 검증

- **curl 은 예전 소스를 받을 수 있다**(쿠키 없음, 캐시). 적용 확인은 playwright 실제 브라우저로 한다. `scripts/live_check.py`, `verify_applied.py`.
- 모바일은 iPhone UA + `is_mobile`. 카페24는 UA 로 모바일 본문(상세설명 모바일 사본)을 따로 내보낸다.
- 폭: 390(모바일), 800(태블릿, 1024 이하 탭 구조), 1300 또는 1440(PC). 브레이크포인트는 767/768, 1024/1025.
- **WebKit(사파리) 따로 확인.** 사파리 전용 버그 전례: 그리드 안 aspect-ratio 사진의 줄 높이를 낮게 잡아 글자를 침범.
- 코드 주입 검증: 실제 페이지를 열고 새 CSS/JS 를 넣어 측정한다. 기존 블록을 대체하는 경우는 HTML 문자열에 찾기/바꾸기를 실제로 수행한 뒤 그 문서를 띄워(route 로 응답 가로채기) 찾기 1건, 활성 스타일 1개를 확인한다.
- 측정 항목: 가로 넘침(scrollWidth > clientWidth), 깨진 이미지(naturalWidth 0), 콘솔 오류, 요소 겹침(elementFromPoint), 클릭 후 상태.
- 지연로딩: 상세설명 이미지는 `ec-data-src` 지연로딩. 350px 간격으로 스크롤해 로딩시킨 뒤 검사.
- **https 라이브 페이지에서 `http://127.0.0.1` 로 fetch 하면 사설망 차단으로 탭이 먹통.** 라이브 주입에 로컬 fetch 금지.
- 백그라운드 탭은 `visibilityState hidden` 이라 IntersectionObserver, smooth scroll, hover 가 안 돈다. 스크롤 등장, 호버 검증은 실제 휠 스크롤과 좌표 이동으로.
- playwright 요소 스크린샷은 뷰포트 밖 큰 요소에서 배경을 잘못 찍는다. `full_page=True` + `clip` 사용.
- 부모 문서에서 iframe 에 document.write 하면 iframe URL 이 부모 URL 로 바뀐다. srcdoc 을 쓴다.
- 외부 스크립트(GA collect, alphwidget) ERR_TIMED_OUT 은 우리 코드와 무관하다.

## 5. 스킨 구조 사실 (basic 스킨)

- **반응형 단일 스킨.** CSS 한 번으로 모바일, PC 동시 적용.
- 상품카드: `.prdList__item > .thumbnail > a>img + .likeButton + .badge + .icon__box > span.wish/.cart/.option`. 1024 이하에서 `.icon__box` 는 display none.
- 목록 가격 줄은 `ul.spec > li`, 항목 구분은 `.title` 글자(간략설명/판매가/소비자가)뿐이라 스크립트로 분류해 클래스(ssd-brief, ssd-sale, ssd-consumer, ssd-off)를 붙여 쓴다.
- 정렬 `select#selArray` 는 jQuery change 바인딩. 커스텀 UI 는 select 를 숨긴 채 값 변경 + change 이벤트 발생.
- 관심상품은 `layout.js` 전역 `ifmore()` 가 `.wish` 에 `on` 을 붙인다. 하트 채움은 `.wish.on`.
- 상세 갤러리 원본은 `.xans-product-mobileimage li img`. PC 썸네일은 `small` 을 `big` 으로 치환.
- 상세 옵션 버튼은 `ul.ec-product-button > li > a > span` 한 덩어리 텍스트(`X-Small X스몰`).
- 상세 하단: PC 는 `#prdDetail`, `#prdReview`, `#prdQnA`, `#prdInfo` 가 모두 펼쳐지고 섹션마다 `.detail_tab` 4칸 탭이 반복. **1024 이하는 `#tabProduct`(상세정보/구매안내/상품후기/상품문의) 탭 전환이고 나머지 섹션은 display none.** 앵커 링크(`#guide`, `#prdInfo`)는 탭을 먼저 눌러야 동작한다.
- 에디봇 스마트배너는 편집기 index.html 에 없고 앱이 렌더 시 삽입한다. 렌더된 클래스(`.xans-smart-banner-admin-RESxxxxx`)를 기준으로 스크립트 처리.
- 상품별 색상이 옵션이 아니라 개별 상품이면 목록 템플릿에 형제 색상 데이터가 없다. 상품명 `라인명 | 색상명` 파싱 + 스크립트 색상표로 스와치를 만든다.
- 스킨 `normalmenu.js` 무한스크롤은 `.xans-product-listmore` 가 없으면(상품이 한 페이지에 다 들어가면) offset 을 읽다 오류. length 가드 필요.
- 세트상품(`xans-product-setproduct`)은 판매가가 구성상품 합계 + 세트할인 자동계산이라 **소비자가 항목이 없고 취소선도 안 나오는 것이 카페24 사양.** 목록에는 세트할인 데이터가 안 넘어온다.
- 소비자가 값이 있으면 판매가와 같아도 취소선 줄이 나온다. 없애려면 소비자가를 0/공란으로.
- 소비자가 입력칸 자체가 안 보이면: 쇼핑몰 설정 > 상품 설정 > 상품 보기 설정 > 상품 정보 표시 설정에서 소비자가가 '표시 안함'인 상태.

## 6. 에디봇 상세설명

- HTML 모드 붙여넣기는 div/section 의 class 를 유지하지만 `<style>` 블록은 지우고 인라인으로 굳힌다. 그래서 **CSS 는 layout.html 에 `#prdDetail` 스코프로 한 번, 에디봇에는 클래스만 있는 HTML.** 인라인 style 은 쓰지 않는다(색 점도 `.sd__pc-HEX` 클래스로).
- img `/web/...` 경로는 저장 시 `//ecimg.cafe24img.com/<몰ID>/<계정>/web/...` 로 바뀌고 src 는 `ec-data-src` 지연로딩(1x1 투명 자리표시)이 된다.
- 파일업로더 파일은 `도메인/web/...` 로는 404, **ecimg CDN 주소로만 열린다.** CSS 배경에는 CDN 주소를 직접.
- **모바일 상세설명은 PC 본문을 자동 변환한 별도 사본**(NNEditor/mobile 로 이미지 재업로드)이고 img 의 class 와 alt 를 지운다. 이미지 스타일은 부모 선택자로.
- 스킨에 `.productDetail img{max-width:100% !important;height:auto !important}` 가 있어 이미지 크기는 `!important` + `#prdDetail .sd img` 이상 명시도.
- `.sd p{margin:0}` 같은 리셋은 `:where()` 로 감싸 명시도 0 으로(안 그러면 본문 여백 규칙을 이김).
- b/i 는 편집기가 strong/em 으로 바꿀 수 있어 `:is(b,strong)` 처리.
- 1024 이하에서 `.ssd-pdp > .infoArea` 가 sticky(쌓임맥락)라 구매 고정바(#orderFixArea)가 상세설명 아래로 깔린다. `.ssd-pdp > .infoArea{z-index:50}`.
- 사이트 폰트는 Montserrat 400/500/700 만 로드된다. 600 이 필요하면 @import.

## 7. 깜빡임(FOUC) 방지

커스텀 스크립트가 화면을 다 고칠 때까지 body 를 가렸다가 한 번에 보여 준다(`깜빡임 방지` / `깜빡임 방지 해제` 블록). 스크립트가 멈춰도 1초 뒤 무조건 보이도록 animation 안전장치가 있다. 첫 화면 사진(상세 갤러리 첫 장)은 가림 대상에서 빼는 것이 좋다.
