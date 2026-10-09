#!/usr/bin/env python3
"""페이지에 들어간 커스텀 블록(<!-- SILVERSYD/BRAND 이름 시작/끝 -->)을 순서대로 보여 준다.

사용:
  python3 list_blocks.py https://silversyd.com/
  python3 list_blocks.py https://silversyd.com/product/detail.html?product_no=64 --mobile
  python3 list_blocks.py 페이지.html --get "배송교환 안내 링크" > block.html
주의: curl/urllib 은 캐시된 예전 소스를 받을 때가 있다. 적용 직후 확인은 verify_applied.py(브라우저)로.
"""
import re, sys
from _fetch import read

PAT = re.compile(r"<!-- ((?:SILVERSYD|BRAND|SSD)[^>]*?) (시작|끝)([^>]*)-->")


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__); sys.exit(2)
    html = read(a[0], mobile="--mobile" in sys.argv)
    if "--get" in sys.argv:
        name = a[1]
        m1 = re.search(r"<!-- [^>]*" + re.escape(name) + r" 시작[^>]*-->", html)
        m2 = re.search(r"<!-- [^>]*" + re.escape(name) + r" 끝[^>]*-->", html[m1.end():]) if m1 else None
        if not (m1 and m2):
            print("블록을 찾지 못함:", name, file=sys.stderr); sys.exit(1)
        sys.stdout.write(html[m1.start(): m1.end() + m2.end()] + "\n")
        return
    seen, n = set(), 0
    for m in PAT.finditer(html):
        key = (m.group(1), m.group(2))
        if m.group(2) != "시작" or key in seen:
            continue
        seen.add(key); n += 1
        extra = m.group(3).strip()
        print(f"{n:2d}. {m.group(1)}" + (f"  {extra}" if extra else ""))
    print(f"\n총 {n}개 (페이지 길이 {len(html):,}자)")


if __name__ == "__main__":
    main()
