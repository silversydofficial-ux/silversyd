#!/usr/bin/env python3
"""사용자가 붙여 넣은 코드가 원본과 같은지 실제 브라우저 소스로 확인한다.

사용: python3 verify_applied.py URL 원본블록파일 [--mobile]
원본블록파일은 <!-- ... 시작 --> 부터 <!-- ... 끝 --> 까지(찾기 앵커 줄은 있어도 되고 없어도 됨).
curl 은 캐시된 예전 소스를 받을 때가 있어 playwright 로 연다(없으면 urllib 로 대체).
"""
import re, sys, difflib


def page_source(url, mobile):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        from _fetch import read
        print("(playwright 없음, urllib 로 받음: 캐시된 소스일 수 있음)")
        return read(url, mobile)
    from _fetch import UA_MO
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(user_agent=UA_MO if mobile else None)
        pg = ctx.new_page()
        resp = pg.goto(url, wait_until="domcontentloaded")
        html = resp.text()
        b.close()
        return html


def norm(s):
    return [l.rstrip() for l in s.replace("\r\n", "\n").split("\n") if l.strip()]


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if len(a) < 2:
        print(__doc__); sys.exit(2)
    src = open(a[1], encoding="utf-8").read()
    m = re.search(r"<!-- ([^>]*?) 시작[^>]*-->", src)
    if not m:
        sys.exit("원본에서 '<!-- 이름 시작 -->' 주석을 찾지 못함")
    name = m.group(1)
    src_block = src[m.start():]
    e = re.search(r"<!-- " + re.escape(name) + r" 끝[^>]*-->", src_block)
    src_block = src_block[: e.end()] if e else src_block
    live = page_source(a[0], "--mobile" in sys.argv)
    n = live.count("<!-- " + name + " 시작")
    print(f"블록 '{name}' 라이브 개수: {n}")
    if n == 0:
        sys.exit(1)
    i = live.index("<!-- " + name + " 시작")
    j = re.search(r"<!-- " + re.escape(name) + r" 끝[^>]*-->", live[i:])
    live_block = live[i: i + j.end()] if j else live[i: i + len(src_block) + 2000]
    d = list(difflib.unified_diff(norm(src_block), norm(live_block), "원본", "라이브", lineterm="", n=1))
    if not d:
        print("원본과 동일 (공백 줄 제외)" + ("" if n == 1 else "  !! 같은 블록이 여러 번 들어가 있음"))
    else:
        print("차이 있음:"); print("\n".join(d[:80]))
        sys.exit(1)


if __name__ == "__main__":
    main()
