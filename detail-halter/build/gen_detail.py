"""홀터넥 탑 상세페이지 시안 생성기.

img/*.webp 를 data URI 로 박아 ../out/halter_detail.html 하나로 만든다.
이미지를 바꾸려면 I 딕셔너리의 파일명만 바꾸면 된다.
홀터넥 4개 상품(51 블랙, 53 차콜, 54 밀크블루, 55 버건디)은 같은 페이지를 쓴다.

usage: python3 gen_detail.py
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

# 키 -> 파일명 (img/ 기준). 교체는 여기서만.
I = {k: f"{k}.webp" for k in (
    "hero front back side full detail cut1 cut2 cut3 look1 look2 look3 look4 look5 "
    "ghost col_black col_charcoal col_burgundy col_blue fab0 fab1 fab2 fab3 "
    "z1 z2 z3 stage brand shorts set").split()}
TEMP = {"stage", "brand"}  # 생성 전 임시 이미지


def uri(key):
    data = (IMG / I[key]).read_bytes()
    return "data:image/webp;base64," + base64.b64encode(data).decode()


def img(key, alt, cls=""):
    badge = '<span class="temp">임시 이미지</span>' if key in TEMP else ""
    return f'<figure class="ph {cls}"><img src="{uri(key)}" alt="{alt}">{badge}</figure>'


# ---- 기구 실루엣 / 짐 키트 아이콘 (선 아이콘, 실사 누끼로 교체 예정) ----
SVG = {
    "RACK": '<path d="M10 6v52M54 6v52M6 58h52M10 14h44M10 34h6M48 34h6"/><path d="M4 30h56" stroke-width="3"/>',
    "BARBELL": '<path d="M4 32h56"/><rect x="12" y="20" width="6" height="24"/><rect x="46" y="20" width="6" height="24"/><rect x="7" y="25" width="5" height="14"/><rect x="52" y="25" width="5" height="14"/>',
    "PLATE": '<circle cx="32" cy="32" r="24"/><circle cx="32" cy="32" r="16"/><circle cx="32" cy="32" r="4"/>',
    "BELT": '<path d="M6 24c8-4 44-4 52 0v16c-8 4-44 4-52 0z"/><rect x="26" y="25" width="12" height="14"/><path d="M32 25v14"/>',
    "STRAP": '<path d="M14 8v34a10 10 0 0 0 20 0V8M24 8v30"/><path d="M40 20h16v28H40z"/>',
    "KETTLEBELL": '<path d="M22 22a10 10 0 0 1 20 0"/><path d="M18 24h28l6 14a20 20 0 0 1-40 0z"/>',
}
KIT = {
    "HEADPHONES": '<path d="M12 40V32a20 20 0 0 1 40 0v8"/><rect x="8" y="38" width="10" height="16"/><rect x="46" y="38" width="10" height="16"/>',
    "TUMBLER": '<path d="M20 10h24l-3 46H23z"/><path d="M20 18h24M26 4h12v6H26z"/>',
    "YOGA MAT": '<circle cx="18" cy="32" r="12"/><circle cx="18" cy="32" r="5"/><path d="M18 20h38v24H18"/>',
    "LIFTING SHOES": '<path d="M6 44h52v6H6zM6 44l4-16h14l8 6h14l12 4v6"/><path d="M14 28l6-8h8"/>',
    "DUMBBELL": '<path d="M18 32h28"/><rect x="8" y="22" width="10" height="20"/><rect x="46" y="22" width="10" height="20"/><rect x="4" y="26" width="4" height="12"/><rect x="56" y="26" width="4" height="12"/>',
}


def icon(name, paths):
    return (f'<div class="ico"><svg viewBox="0 0 64 64" aria-hidden="true">{paths}</svg>'
            f'<span>{name}</span></div>')


FAQ = [
    ("패드는 빼서 세탁할 수 있나요?", "가슴 패드는 안쪽에 내장되어 있습니다. 세탁 후에는 패드 모양을 손으로 정리한 뒤 뉘어서 말려 주세요."),
    ("평소 55 사이즈인데 어떤 걸 고르면 될까요?", "가슴둘레 기준으로 S를 권해요. 압박감이 있는 핏을 좋아하지 않으면 한 사이즈 크게 고르셔도 됩니다."),
    ("데드리프트나 바벨 로우를 할 때 앞이 들뜨지 않나요?", "앞판이 이중 구조라 상체를 숙여도 가슴 쪽이 벌어지지 않습니다. 밑단 밴딩이 허리선을 잡아 줘요."),
    ("홀터 스트랩 때문에 목이 아프지 않나요?", "스트랩 폭을 넓게 잡아 하중이 목 뒤 한 점에 몰리지 않습니다. 오버헤드 프레스처럼 팔을 드는 동작에서도 당김이 적어요."),
    ("밝은 컬러는 비치지 않나요?", "밀크블루도 안감과 패드가 함께 들어가 있어 운동 중 비침 걱정을 덜었습니다."),
    ("세탁은 어떻게 하나요?", "30℃ 이하 찬물에서 단독 손세탁해 주세요. 표백제, 건조기, 다림질은 원단을 상하게 하니 피해 주세요. 그늘에서 뉘어서 말리면 됩니다."),
    ("쇼츠와 함께 사면 할인이 되나요?", "셋업으로 구매하면 63,000원으로 단품 두 개보다 5,000원 저렴합니다."),
]


def faq_html():
    return "".join(
        f'<details class="qa"{" open" if i == 0 else ""}><summary><span class="qn">Q{i + 1:02d}</span>{q}</summary><p>{a}</p></details>'
        for i, (q, a) in enumerate(FAQ))


CSS = """
/* 레이아웃: 카페24 상세 폭 860px 단일 칼럼. 사진 면과 여백으로 구분하고 가로선은 쓰지 않는다 */
:root{
  --ink:#0D0D0D; --ink2:#3F3F3F; --sub:#7D7D7D; --faint:#B3B3B3; --soft:#F3F2F0; --inv:#0B0B0B;
  --paper:#FFFFFF; --band:#E4E0DA; --look:#B2AEA8;
  --en:"Montserrat",Arial,sans-serif; --ko:"Noto Sans KR",Arial,sans-serif;
  --r:0; --sx:48px; --sy:64px;
  color-scheme:light;
}
@media (max-width:640px){:root{--sx:20px;--sy:40px}}
html,body{background:#E9E8E6}
body{font-family:var(--ko);color:var(--ink);-webkit-font-smoothing:antialiased;padding-inline:0}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:9;display:flex;gap:8px;justify-content:center;padding:8px 16px;background:#E9E8E6}
.bar button{font:600 11px/1 var(--en);letter-spacing:.16em;padding:8px 16px;border:1px solid var(--ink);background:var(--paper);color:var(--ink);cursor:pointer;border-radius:0}
.bar button[aria-pressed="true"]{background:var(--ink);color:var(--paper)}
.bar button:focus-visible,summary:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.page{max-width:860px;margin:0 auto;background:var(--paper);overflow:hidden;transition:max-width .3s}
.page.mo{max-width:390px}
.page.mo{--sx:20px;--sy:40px}
@media (prefers-reduced-motion:reduce){.page{transition:none}}
section{padding:var(--sy) var(--sx)}
.full{padding-inline:0}
.ph{margin:0;position:relative;background:var(--soft)}
.ph img{display:block;width:100%;height:100%;object-fit:cover;border-radius:var(--r)}
.temp{position:absolute;top:8px;right:8px;font:600 10px/1 var(--ko);background:#C8102E;color:#fff;padding:4px 8px}
.lab{font:600 11px/1 var(--en);letter-spacing:.16em;text-transform:uppercase;color:var(--sub);margin:0 0 16px}
.big{font:700 clamp(34px,6.4vw,54px)/.94 var(--en);letter-spacing:-.035em;text-transform:uppercase;margin:0;text-wrap:balance}
.big em{font-style:normal;color:var(--faint)}
.h{font:600 clamp(22px,4vw,34px)/1.05 var(--en);letter-spacing:-.02em;text-transform:uppercase;margin:0 0 16px;text-wrap:balance}
.st{font:600 17px/1.2 var(--en);margin:0 0 8px}
.num{font:700 34px/1 var(--en);color:#D9D8D5;margin:0 0 8px}
p,.body{font:400 14px/1.8 var(--ko);letter-spacing:-.01em;color:var(--ink2);margin:0}
.aux{font:400 12.5px/1.7 var(--ko);color:var(--sub)}
.cap{font:400 11.5px/1.5 var(--ko);color:var(--sub)}
.en{font-family:var(--en)}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:0}
.g2>*,.g3>*,.g4>*{min-width:0}
.page.mo .g2,.page.mo .g3{grid-template-columns:1fr}
@media (max-width:640px){.g2,.g3{grid-template-columns:1fr}}
.r34{aspect-ratio:3/4}.r11{aspect-ratio:1}.r43{aspect-ratio:4/3}.r219{aspect-ratio:21/9}

/* 1 인트로 */
.intro{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start}
.page.mo .intro{grid-template-columns:1fr}
@media (max-width:640px){.intro{grid-template-columns:1fr}}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}
.chip{font:600 10.5px/1 var(--en);letter-spacing:.12em;padding:8px 12px;border:1px solid var(--ink)}
.spec3{display:grid;gap:8px;margin:0 0 24px}
.spec3 div{display:grid;grid-template-columns:72px 1fr;gap:8px;align-items:baseline}
.spec3 b{font:600 11px/1 var(--en);letter-spacing:.12em;text-transform:uppercase}
.spec3 span{font:400 13px/1.6 var(--ko);color:var(--ink2)}
.tbl{width:100%;border-collapse:collapse;background:var(--soft)}
.tbl caption{text-align:left;font:600 11px/1 var(--en);letter-spacing:.16em;padding:0 0 8px}
.tbl th,.tbl td{text-align:left;padding:8px 12px;font:400 12.5px/1.6 var(--ko);vertical-align:top}
.tbl th{font-weight:500;color:var(--sub);width:72px;white-space:nowrap}
.hero{position:relative;background:var(--soft);aspect-ratio:3/4}
.hero img{position:absolute;bottom:0;left:50%;transform:translateX(-50%);height:96%;width:auto;max-width:none}
.note{position:absolute;font:500 10.5px/1.35 var(--ko);color:var(--ink);display:flex;align-items:center;gap:6px;max-width:44%}
.note>span{background:rgba(255,255,255,.88);padding:4px 6px}
.note i{flex:none;width:7px;height:7px;border-radius:50%;background:var(--ink);box-shadow:0 0 0 3px rgba(255,255,255,.8)}
.note b{font:600 9.5px/1 var(--en);letter-spacing:.14em;display:block;margin-bottom:2px}

/* 2 기구 스트립 */
.strip{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;padding:24px var(--sx);background:var(--soft)}
.ico{display:grid;justify-items:center;gap:8px}
.ico svg{width:40px;height:40px;fill:none;stroke:var(--ink);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.ico span{font:600 9px/1 var(--en);letter-spacing:.14em;color:var(--sub)}

/* 반전 섹션 */
.inv{background:var(--inv);color:#F2F2F2}
.inv p{color:#BDBDBD}.inv .lab{color:#8C8C8C}.inv .big em{color:#5E5E5E}.inv .num{color:#2E2E2E}
.inv .ph{background:#151515}
.list{display:grid;gap:24px}
.list .st{color:inherit}

/* 4 시리즈 카드 */
.card .ph{margin-bottom:12px}
.card .st{margin:0 0 4px}
.price{font:600 13px/1 var(--en);letter-spacing:.02em}
.now{font:600 9.5px/1 var(--en);letter-spacing:.14em;background:var(--ink);color:#fff;padding:4px 6px;margin-left:6px;vertical-align:2px}

/* 5 사양 */
.specl{display:grid;gap:0}
.specl div{display:grid;grid-template-columns:96px 1fr;gap:12px;padding:12px 0}
.specl div:nth-child(odd){background:var(--soft);padding-inline:12px;margin-inline:-12px}
.specl b{font:600 11px/1.6 var(--en);letter-spacing:.12em;text-transform:uppercase}
.specl span{font:400 13.5px/1.6 var(--ko);color:var(--ink2)}

/* 7 디테일 교차 */
.alt{display:grid;gap:40px}
.alt .row{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center}
.alt .row:nth-child(even) .ph{order:2}
.page.mo .alt .row{grid-template-columns:1fr}.page.mo .alt .row .ph{order:0}
@media (max-width:640px){.alt .row{grid-template-columns:1fr}.alt .row .ph{order:0}}

/* 8 누끼 스택 */
.stack{position:relative;padding:var(--sy) var(--sx) 0;background:var(--paper)}
.stack .band{position:absolute;left:0;right:0;bottom:0;height:46%;background:var(--band)}
.stack .row{position:relative;display:grid;grid-template-columns:repeat(3,1fr);align-items:end;gap:0}
.stack img{display:block;width:100%;height:auto}
.stack .tag{position:absolute;bottom:16px;left:var(--sx);right:var(--sx);display:flex;justify-content:space-between;font:600 10px/1 var(--en);letter-spacing:.16em;color:var(--ink2)}

/* 9 LOOK 콜라주 */
.look{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;padding:0}
.look .ph{background:var(--look)}
.look .a{grid-column:span 3;aspect-ratio:3/4}.look .b{grid-column:span 3;aspect-ratio:3/4}
.look .c,.look .d,.look .e{grid-column:span 2;aspect-ratio:3/4}
.look .n{position:absolute;top:12px;left:12px;font:700 22px/1 var(--en);color:#fff;letter-spacing:-.02em}
.lookband{background:var(--band);padding:24px var(--sx);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:baseline}

/* 10 컬러 */
.colors .ph{aspect-ratio:3/4}
.colors .ph figcaption{position:absolute;left:12px;bottom:12px;font:600 10.5px/1.3 var(--en);letter-spacing:.14em;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.colors .ph figcaption span{display:block;font:400 11px/1.4 var(--ko);letter-spacing:0}
.ghosts{display:grid;grid-template-columns:repeat(4,1fr);gap:0;background:#fff}
.ghosts .ph{background:#fff;aspect-ratio:3/4}
.ghosts .ph img{object-fit:contain}

/* 12 짐 키트 */
.kit{display:grid;grid-template-columns:repeat(6,1fr);grid-auto-rows:minmax(80px,auto);gap:8px;background:var(--soft);padding:24px}
.kit .ph{background:transparent}
.kit .ph img{object-fit:contain}
.kit .k1{grid-column:1/4;grid-row:1/4}.kit .k2{grid-column:4/7;grid-row:1/3}
.kit .ico{align-content:center;background:var(--paper);padding:16px 8px}
.kit .ico svg{width:48px;height:48px;stroke-width:1.6}
.kit .i1{grid-column:4/5}.kit .i2{grid-column:5/6}.kit .i3{grid-column:6/7}.kit .i4{grid-column:1/3}.kit .i5{grid-column:3/5}

/* 14 사이즈 */
.size{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
.size th,.size td{padding:12px 8px;text-align:center;font:400 13px/1 var(--ko)}
.size thead th{font:600 11px/1 var(--en);letter-spacing:.14em;background:var(--ink);color:#fff}
.size tbody tr:nth-child(odd){background:var(--soft)}
.size tbody th{font-weight:500;text-align:left;padding-left:12px}
.scroll{overflow-x:auto}
.fit{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:24px}
.fit>div{background:var(--soft);padding:16px}
.page.mo .fit{grid-template-columns:1fr}
@media (max-width:640px){.fit{grid-template-columns:1fr}}

/* 15 FAQ */
.qa{background:var(--soft);margin-bottom:8px}
.qa summary{list-style:none;cursor:pointer;padding:16px;font:500 14px/1.5 var(--ko);display:flex;gap:12px;align-items:baseline}
.qa summary::-webkit-details-marker{display:none}
.qa summary::after{content:"+";margin-left:auto;font:400 18px/1 var(--en)}
.qa[open] summary::after{content:"\\2212"}
.qa .qn{font:700 11px/1 var(--en);letter-spacing:.1em;color:var(--sub)}
.qa p{padding:0 16px 16px 52px}

/* 16 브랜드 */
.brand{position:relative;background:#000;color:#fff}
.brand .ph{aspect-ratio:4/5;background:#000}
.brand .ph img{opacity:.78}
.brand .over{position:absolute;left:var(--sx);right:var(--sx);bottom:var(--sy)}
.brand .shine{color:#fff;font:700 clamp(44px,9vw,84px)/.9 var(--en);letter-spacing:-.04em;margin:0 0 16px;text-transform:uppercase}
.brand .ko{font:400 14px/1.8 var(--ko);color:#D0D0D0;max-width:30em}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:32px var(--sx) var(--sy);background:#000;color:#fff}
.stats b{display:block;font:700 18px/1.1 var(--en);letter-spacing:-.01em;margin-bottom:8px}
.stats span{font:400 11.5px/1.6 var(--ko);color:#9A9A9A}
.page.mo .stats{grid-template-columns:1fr 1fr}
@media (max-width:640px){.stats{grid-template-columns:1fr 1fr}}
"""

JS = """
const pg=document.querySelector('.page');
document.querySelectorAll('.bar button').forEach(b=>b.addEventListener('click',()=>{
  const mo=b.dataset.v==='mo'; pg.classList.toggle('mo',mo);
  document.querySelectorAll('.bar button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
}));
"""


def build():
    strip = "".join(icon(n, p) for n, p in SVG.items())
    kit_icons = "".join(
        f'<div class="ico i{i}"><svg viewBox="0 0 64 64" aria-hidden="true">{p}</svg><span>{n}</span></div>'
        for i, (n, p) in enumerate(KIT.items(), 1))
    colors = [("fab0", "BLACK", "블랙", "51"), ("fab1", "CHARCOAL", "차콜", "53"),
              ("fab2", "MILK BLUE", "밀크블루", "54"), ("fab3", "BURGUNDY", "버건디", "55")]
    color_tiles = "".join(
        f'<figure class="ph"><img src="{uri(k)}" alt="{ko} 원단 확대">'
        f'<figcaption>{en}<span>{ko}</span></figcaption></figure>' for k, en, ko, _ in colors)
    ghost_tiles = "".join(img(k, f"{ko} 홀터넥 탑 단독") for k, ko in (
        ("col_black", "블랙"), ("col_charcoal", "차콜"), ("col_blue", "밀크블루"), ("col_burgundy", "버건디")))

    html = f"""<title>쉐이프업 홀터넥 탑 상세</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<style>{CSS}</style>
<div class="bar" role="group" aria-label="미리보기 폭">
  <button type="button" data-v="pc" aria-pressed="true">PC 860</button>
  <button type="button" data-v="mo" aria-pressed="false">MOBILE 390</button>
</div>
<main class="page">

<!-- 1 인트로 -->
<section class="intro">
  <div>
    <p class="lab">Woman Shape-up Series</p>
    <h2 class="big">Shape Up<br><em>Halter Neck</em></h2>
    <div class="chips"><span class="chip">OPEN BACK</span><span class="chip">BUILT-IN PAD</span><span class="chip">SEAMLESS KNIT</span><span class="chip">3D LINE</span></div>
    <p class="body" style="margin-bottom:24px">등은 열고 앞은 단단히 잡았습니다. 세트 사이에 숨을 고를 때도, 바벨을 다시 잡을 때도 자세가 흐트러지지 않는 홀터넥 탑이에요.</p>
    <div class="spec3">
      <div><b>Fabric</b><span>나일론 90%, 스판덱스 10%</span></div>
      <div><b>Support</b><span>내장 패드와 이중 앞판</span></div>
      <div><b>Length</b><span>허리선까지 오는 기장, 크롭이 아닙니다</span></div>
    </div>
    <table class="tbl"><caption>SPECIFICATION</caption>
      <tr><th>상품명</th><td>우먼 쉐이프업 홀터넥 탑</td></tr>
      <tr><th>소재</th><td>겉감 나일론 90%, 스판덱스 10%<br>안감 폴리에스터 100%</td></tr>
      <tr><th>컬러</th><td>블랙, 차콜, 밀크블루, 버건디</td></tr>
      <tr><th>사이즈</th><td>S, M, L</td></tr>
      <tr><th>제조국</th><td>중국</td></tr>
    </table>
  </div>
  <div class="hero">
    <img src="{uri('hero')}" alt="차콜 홀터넥 탑 정면 착용">
    <span class="note" style="top:21%;right:2%"><i></i><span><b>HALTER STRAP</b>목 뒤로 하중을 나눠요</span></span>
    <span class="note" style="top:41%;left:2%"><i></i><span><b>3D LINE</b>절개선이 허리 라인을 세웁니다</span></span>
    <span class="note" style="top:62%;right:2%"><i></i><span><b>HEM BAND</b>숙여도 말려 올라가지 않아요</span></span>
  </div>
</section>

<!-- 2 기구 스트립 -->
<div class="strip">{strip}</div>

<!-- 3 블랙 반전 -->
<section class="inv full" style="padding-bottom:0">
  <div style="padding:0 var(--sx) 32px">
    <p class="lab">For Heavy Days</p>
    <h2 class="big">Lift Heavy<br><em>Wear Light</em></h2>
  </div>
  {img('stage', '어두운 짐에서 운동 중인 착용 컷', 'r219')}
</section>
<section class="inv">
  <div class="g2" style="align-items:center">
    {img('back', '오픈백 뒷모습 흑백', 'r34')}
    <div class="list">
      <div><p class="num">01</p><p class="st">Open Back</p><p>데드리프트 락아웃에서 견갑을 모을 때 등 근육이 그대로 보입니다. 거울로 자세를 확인하는 리프터를 위한 설계예요.</p></div>
      <div><p class="num">02</p><p class="st">Front Support</p><p>앞판을 이중으로 잡아 바벨 로우처럼 상체를 숙이는 동작에서도 가슴 쪽이 들뜨지 않습니다.</p></div>
      <div><p class="num">03</p><p class="st">No Ride-Up</p><p>오버헤드 프레스로 팔을 끝까지 올려도 밑단 밴딩이 허리선을 붙잡아 줘요.</p></div>
    </div>
  </div>
</section>

<!-- 4 쉐이프업 시리즈 -->
<section>
  <p class="lab">Shape-up Series</p>
  <div class="g3">
    <div class="card">{img('ghost', '홀터넥 탑 단독', 'r34')}<p class="st">Halter Top<span class="now">NOW</span></p><p class="price">36,000</p></div>
    <div class="card">{img('shorts', '3부 쇼츠 단독', 'r34')}<p class="st">3/10 Shorts</p><p class="price">32,000</p></div>
    <div class="card">{img('set', '셋업 4컬러', 'r34')}<p class="st">Set-up</p><p class="price">63,000</p></div>
  </div>
</section>

<!-- 5 사양 -->
<section style="background:var(--soft)">
  <div class="g2">
    {img('front', '홀터넥 탑 상체 정면', 'r11')}
    <div>
      <h2 class="h">Spec Sheet</h2>
      <div class="specl" style="background:var(--paper);padding:0 12px">
        <div><b>Shell</b><span>나일론 90%, 스판덱스 10%</span></div>
        <div><b>Lining</b><span>폴리에스터 100%</span></div>
        <div><b>Pad</b><span>가슴 패드 내장</span></div>
        <div><b>Neck</b><span>목 뒤로 잠그는 홀터 스트랩</span></div>
        <div><b>Length</b><span>허리선 기장</span></div>
        <div><b>Logo</b><span>왼쪽 밑단, 폭 3.5cm</span></div>
      </div>
    </div>
  </div>
</section>

<!-- 6 Three Reasons -->
<section>
  <p class="lab">Why This Top</p>
  <h2 class="h">Three Reasons</h2>
  <div class="g3">
    <div>{img('detail', '등판 착용 디테일', 'r34')}<p class="num" style="margin-top:16px">01</p><p class="st">Seamless Knit</p><p class="aux">봉제선 대신 편직으로 짜서 랫풀다운 중 겨드랑이 쪽이 쓸리지 않아요.</p></div>
    <div>{img('side', '측면 착용', 'r34')}<p class="num" style="margin-top:16px">02</p><p class="st">3D Line</p><p class="aux">빅로고 대신 절개선이 브랜드를 말합니다. 옆에서 보면 허리 라인이 서요.</p></div>
    <div>{img('full', '전신 착용', 'r34')}<p class="num" style="margin-top:16px">03</p><p class="st">Daily to Gym</p><p class="aux">허리선까지 오는 기장이라 운동 전후 그대로 입고 다녀도 어색하지 않습니다.</p></div>
  </div>
</section>

<!-- 7 The Details -->
<section style="background:var(--soft)">
  <p class="lab">Close Look</p>
  <h2 class="h">The Details</h2>
  <div class="alt">
    <div class="row">{img('z1', '홀터 스트랩 확대', 'r43')}<div><p class="num">01</p><p class="st">Halter Strap</p><p>목 뒤로 넓게 감기는 스트랩이 하중을 한 점에 몰지 않습니다.</p></div></div>
    <div class="row">{img('z2', '내장 패드 확대', 'r43')}<div><p class="num">02</p><p class="st">Built-in Pad</p><p>패드가 안쪽에 자리 잡고 있어 따로 챙길 필요가 없어요. 셔링이 가슴 라인을 모아 줍니다.</p></div></div>
    <div class="row">{img('z3', '시그니처 로고 확대', 'r43')}<div><p class="num">03</p><p class="st">Signature Mark</p><p>왼쪽 밑단에 작게 들어간 다이아몬드 마크와 워드마크. 크게 박지 않았습니다.</p></div></div>
    <div class="row">{img('cut3', '등판 밴드 착용', 'r34')}<div><p class="num">04</p><p class="st">Back Band</p><p>등 아래쪽 밴드가 몸통을 감싸 상체를 숙여도 옷이 따라 움직여요.</p></div></div>
  </div>
</section>

<!-- 8 누끼 스택 -->
<div class="stack">
  <div class="band"></div>
  <div class="row">
    <img src="{uri('cut1')}" alt="정면 착용 누끼">
    <img src="{uri('cut2')}" alt="측면 착용 누끼">
    <img src="{uri('cut3')}" alt="후면 착용 누끼">
  </div>
  <div class="tag"><span>FRONT</span><span>SIDE</span><span>BACK</span></div>
</div>

<!-- 9 LOOK -->
<div class="look">
  <figure class="ph a"><img src="{uri('look1')}" alt="룩 01"><span class="n">01</span></figure>
  <figure class="ph b"><img src="{uri('look2')}" alt="룩 02"><span class="n">02</span></figure>
  <figure class="ph c"><img src="{uri('look3')}" alt="룩 03"><span class="n">03</span></figure>
  <figure class="ph d"><img src="{uri('look4')}" alt="룩 04"><span class="n">04</span></figure>
  <figure class="ph e"><img src="{uri('look5')}" alt="룩 05"><span class="n">05</span></figure>
</div>
<div class="lookband"><span class="st" style="margin:0">LOOKBOOK</span><span class="cap">차콜 S 착용, 모델 키 000cm</span></div>

<!-- 10 컬러 -->
<section class="full colors" style="padding-bottom:0">
  <div style="padding:0 var(--sx) 24px"><p class="lab">4 Colors</p><h2 class="h" style="margin:0">One Fit, Four Moods</h2></div>
  <div class="g4">{color_tiles}</div>
  <div class="ghosts">{ghost_tiles}</div>
</section>

<!-- 11 Close Up -->
<section class="inv">
  <p class="lab">Macro</p>
  <h2 class="h">Close Up</h2>
  <div class="g3">
    <div>{img('z1', '스트랩 매크로', 'r43')}<p class="cap" style="margin-top:8px">STRAP 목 뒤 스트랩 마감</p></div>
    <div>{img('z2', '패드 매크로', 'r43')}<p class="cap" style="margin-top:8px">PAD 셔링 패드 안감</p></div>
    <div>{img('z3', '밴딩 매크로', 'r43')}<p class="cap" style="margin-top:8px">BAND 밑단 편직과 로고</p></div>
  </div>
</section>

<!-- 12 Gym Kit -->
<section>
  <p class="lab">What's in the Bag</p>
  <h2 class="h">Gym Kit</h2>
  <div class="kit">
    {img('ghost', '홀터넥 탑', 'k1')}
    {img('shorts', '3부 쇼츠', 'k2')}
    {kit_icons}
  </div>
  <p class="cap" style="margin-top:8px">아이콘은 실사 누끼로 교체 예정</p>
</section>

<!-- 13 Complete The Set -->
<section style="background:var(--soft)">
  <div class="g2" style="align-items:center">
    {img('set', '홀터넥 탑과 쇼츠 셋업', 'r34')}
    <div>
      <p class="lab">Set-up</p>
      <h2 class="h">Complete<br>The Set</h2>
      <p style="margin-bottom:24px">같은 원단, 같은 컬러로 맞춘 3부 쇼츠와 함께 입으면 허리 밴드와 탑 밑단이 한 줄로 이어집니다.</p>
      <p class="price" style="font-size:20px">63,000 <span class="aux en" style="text-decoration:line-through">68,000</span></p>
      <p class="aux">단품 두 개보다 5,000원 저렴해요</p>
    </div>
  </div>
</section>

<!-- 14 Size & Fit -->
<section>
  <p class="lab">Measurements (cm)</p>
  <h2 class="h">Size &amp; Fit</h2>
  <div class="scroll"><table class="size">
    <thead><tr><th></th><th>S</th><th>M</th><th>L</th></tr></thead>
    <tbody>
      <tr><th>가슴 단면</th><td>00</td><td>00</td><td>00</td></tr>
      <tr><th>밑단 단면</th><td>00</td><td>00</td><td>00</td></tr>
      <tr><th>총장</th><td>00</td><td>00</td><td>00</td></tr>
      <tr><th>권장 신장</th><td>155~162</td><td>160~167</td><td>165~172</td></tr>
    </tbody>
  </table></div>
  <p class="cap" style="margin-top:8px">측정 방법에 따라 1~2cm 오차가 있을 수 있습니다.</p>
  <div class="fit">
    <div><p class="st">Fit</p><p class="aux">몸에 붙는 컴프레션 핏. 사이즈 사이라면 작은 쪽을 권해요.</p></div>
    <div><p class="st">Model</p><p class="aux">키 000cm, S 착용</p></div>
    <div><p class="st">Care</p><p class="aux">30℃ 이하 찬물 단독 손세탁. 표백제, 건조기, 다림질 금지. 그늘에서 뉘어서 건조.</p></div>
  </div>
</section>

<!-- 15 FAQ -->
<section style="background:var(--paper);padding-top:0">
  <p class="lab">Questions</p>
  <h2 class="h">FAQ</h2>
  {faq_html()}
</section>

<!-- 16 Brand -->
<div class="brand">
  {img('brand', '흑백 브랜드 이미지')}
  <div class="over">
    <p class="lab" style="color:#9A9A9A">SILVERSYD</p>
    <p class="shine">Shine<br>in Silver</p>
    <p class="ko">은은 처음부터 빛나지 않습니다. 열을 견디고 정제된 다음에야 빛이 나요. 단련한 몸도 그렇습니다.</p>
  </div>
</div>
<div class="stats">
  <div><b>3D CUT</b><span>빅로고 대신 절개선</span></div>
  <div><b>BOLD</b><span>가리지 않고 드러내는 핏</span></div>
  <div><b>BUILT</b><span>단련한 몸을 위한 설계</span></div>
  <div><b>S.Y.D.</b><span>Support Your Dream</span></div>
</div>

</main>
<script>{JS}</script>
"""
    out = OUT / "halter_detail.html"
    out.write_text(html, encoding="utf-8")
    print(out, f"{out.stat().st_size / 1e6:.2f}MB")


if __name__ == "__main__":
    build()
