#!/usr/bin/env python3
"""실제 페이지를 브라우저로 열어 검사한다. 코드 주입, 찾기/바꾸기 시뮬레이션, 클릭 확인, 캡처.

필요: pip install playwright && python3 -m playwright install chromium webkit

사용 예:
  # 지금 라이브 상태 검사 (390, 800, 1300)
  python3 live_check.py "https://silversyd.com/product/detail.html?product_no=64"

  # 새 블록을 body 끝에 넣은 것처럼 검사 + 클릭 확인 + 사파리 엔진도
  python3 live_check.py URL --inject block.html --click ".ssd-pdp__foldLink" --webkit

  # 찾기/바꾸기를 실제 HTML 에 적용한 문서로 검사 (찾기 건수도 보고)
  python3 live_check.py URL --find find.txt --replace replace.txt

  # 클릭 후 확인할 값을 JS 로
  python3 live_check.py URL --click "a.x" --eval "getComputedStyle(document.getElementById('prdInfo')).display"

옵션:
  --widths 390,800,1300   폭 목록. 1024 이하는 iPhone UA + 터치로 연다
  --webkit                WebKit(사파리)으로도 한 번 더
  --inject FILE           body 끝(</body 앞)에 FILE 내용 삽입. 실제 layout.html 맨 아래에 붙인 것과 같은 효과
  --find F --replace R    문서 HTML 에서 F 내용을 R 내용으로 바꿔 띄움(편집기 찾기/바꾸기 재현)
  --click SELECTOR        클릭 전 화면 가운데로 스크롤 후 클릭, 전후 scrollY 와 화면 상단 요소 보고
  --eval JS               마지막에 평가해 출력할 JS 식
  --scroll                지연로딩을 위해 끝까지 350px 간격 스크롤 후 깨진 이미지 검사
  --shots DIR             폭마다 캡처 저장(기본 ./shots)
"""
import argparse, asyncio, json, os, sys

UA_MO = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
END_BODY = "</" + "body>"

MEASURE = """() => {
  const de = document.documentElement;
  const over = [];
  if (de.scrollWidth > de.clientWidth + 1) {
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width && r.right > de.clientWidth + 1 && getComputedStyle(el).position !== 'fixed') {
        over.push((el.id ? '#' + el.id : el.tagName.toLowerCase()) + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '') + ' right=' + Math.round(r.right));
        if (over.length >= 5) break;
      }
    }
  }
  const imgs = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src') && !i.getAttribute('src').startsWith('data:') && i.offsetParent);
  return { scrollWidth: de.scrollWidth, clientWidth: de.clientWidth, overflow: over,
           brokenImages: imgs.slice(0, 5).map(i => i.getAttribute('src')), brokenCount: imgs.length,
           docHeight: de.scrollHeight };
}"""

TOP_AT = """(y) => { const e = document.elementFromPoint(innerWidth / 2, y); return e ? (e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 40) : null; }"""


async def one(pw, engine, url, w, a, report):
    mobile = w <= 1024
    browser = await getattr(pw, engine).launch()
    ctx = await browser.new_context(viewport={"width": w, "height": 844 if mobile else 900},
                                    is_mobile=mobile and engine == "chromium", has_touch=mobile,
                                    user_agent=UA_MO if mobile else None)
    page = await ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)[:160]))
    netfail = []
    page.on("console", lambda m: m.type == "error" and not m.text.startswith("Failed to load resource") and errors.append(m.text[:160]))
    page.on("response", lambda r: r.status >= 400 and netfail.append(f"{r.status} {r.url[:90]}"))
    info = {"engine": engine, "width": w}

    if a.inject or a.find:
        inject = open(a.inject, encoding="utf-8").read() if a.inject else ""
        fnd = open(a.find, encoding="utf-8").read().rstrip("\n") if a.find else None
        rep = open(a.replace, encoding="utf-8").read().rstrip("\n") if a.replace else None

        async def handle(route):
            if route.request.resource_type != "document" or route.request.frame != page.main_frame:
                return await route.continue_()
            resp = await route.fetch()
            body = await resp.text()
            if fnd is not None:
                info["findCount"] = body.count(fnd)
                body = body.replace(fnd, rep, 1)
            if inject:
                i = body.rfind(END_BODY)
                body = body[:i] + inject + body[i:] if i >= 0 else body + inject
            await route.fulfill(response=resp, body=body)
        await page.route("**/*", handle)

    await page.goto(url, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(1500)

    if a.scroll:
        h = await page.evaluate("document.documentElement.scrollHeight")
        for y in range(0, h, 350):
            await page.evaluate(f"window.scrollTo(0,{y})")
            await page.wait_for_timeout(60)
        await page.wait_for_timeout(1200)
        await page.evaluate("window.scrollTo(0,0)")

    info.update(await page.evaluate(MEASURE))

    if a.click:
        el = await page.query_selector(a.click)
        if not el:
            info["click"] = "선택자 없음"
        else:
            await el.evaluate("e => e.scrollIntoView({block:'center'})")
            await page.wait_for_timeout(300)
            before = await page.evaluate("scrollY")
            await page.click(a.click)
            await page.wait_for_timeout(1800)
            info["click"] = {"scrollBefore": round(before), "scrollAfter": round(await page.evaluate("scrollY")),
                             "url": page.url, "textAtTop140": await page.evaluate(TOP_AT, 140)}
    if a.eval:
        info["eval"] = await page.evaluate("() => (" + a.eval + ")")
    info["errors"] = errors[:5]
    info["httpErrors"] = netfail[:5]  # 외부 스크립트(GA, 알파위젯 등) 403/타임아웃은 대개 무관, 우리 파일이면 확인

    os.makedirs(a.shots, exist_ok=True)
    shot = os.path.join(a.shots, f"{engine}_{w}.png")
    await page.screenshot(path=shot)
    info["shot"] = shot
    report.append(info)
    await browser.close()


async def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url")
    p.add_argument("--widths", default="390,800,1300")
    p.add_argument("--webkit", action="store_true")
    p.add_argument("--inject"); p.add_argument("--find"); p.add_argument("--replace")
    p.add_argument("--click"); p.add_argument("--eval")
    p.add_argument("--scroll", action="store_true")
    p.add_argument("--shots", default="shots")
    a = p.parse_args()
    if bool(a.find) != bool(a.replace):
        sys.exit("--find 와 --replace 는 함께 써야 합니다")
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit("playwright 가 없습니다: pip install playwright && python3 -m playwright install chromium webkit")
    report = []
    async with async_playwright() as pw:
        for w in [int(x) for x in a.widths.split(",")]:
            await one(pw, "chromium", a.url, w, a, report)
        if a.webkit:
            for w in [int(x) for x in a.widths.split(",")]:
                await one(pw, "webkit", a.url, w, a, report)
    ok = True
    for r in report:
        bad = r["overflow"] or r["brokenCount"] or r["errors"] or (a.find and r.get("findCount") != 1)
        ok &= not bad
        print(("!!" if bad else "OK"), json.dumps(r, ensure_ascii=False))
    print("\n결과:", "문제 없음" if ok else "확인 필요 항목 있음 (!! 줄)")


if __name__ == "__main__":
    asyncio.run(main())
