#!/usr/bin/env python3
"""카페24 optimizer 번들(/ind-script/optimizer*.php?filename=...) 안의 파일 순서를 복원한다.

사용: python3 decode_optimizer.py URL_또는_HTML파일 [--mobile]
"""
import base64, re, sys, urllib.parse, zlib, html as H
from _fetch import read


def decode(fn):
    b = urllib.parse.unquote(fn)
    b += "=" * (-len(b) % 4)
    raw = base64.urlsafe_b64decode(b)
    s = zlib.decompress(raw, -15).decode("utf-8", errors="replace")
    # 카페24 축약 기호: \x15 파일 구분, \x0c '.', \x0b '_', \n '-'
    s = s.replace("\x0c", ".").replace("\x0b", "_").replace("\n", "-")
    return s.split("\x15")


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__); sys.exit(2)
    page = read(a[0], mobile="--mobile" in sys.argv)
    for m in re.finditer(r'(?:href|src)="([^"]*optimizer[^"]*)"', page):
        url = H.unescape(m.group(1))
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        kind = q.get("type", ["?"])[0]
        print(f"== {kind}  {url[:90]}...")
        for f in q.get("filename", []):
            try:
                for i, p in enumerate(decode(f), 1):
                    if p.strip():
                        print(f"  {i:2d}. {p.strip()}")
            except Exception as e:
                print("  디코드 실패:", e)


if __name__ == "__main__":
    main()
