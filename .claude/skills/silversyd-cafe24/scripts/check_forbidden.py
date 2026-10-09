#!/usr/bin/env python3
"""카페24 편집기가 변조하는 문자열 검사. 전부 0 이어야 전달한다.

사용: python3 check_forbidden.py 파일 [파일...]
  --text  사용자에게 보이는 문구도 검사(가로 대시, 중간점)
종료 코드: 문제가 있으면 1
"""
import sys

CODE = ["$", "?>", "</head", "</body", "http"]
TEXT = ["—", "·"]  # 가로 대시, 중간점


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pats = CODE + (TEXT if "--text" in sys.argv else [])
    if not args:
        print(__doc__)
        sys.exit(2)
    bad = False
    for path in args:
        s = open(path, encoding="utf-8").read()
        print(f"== {path}")
        for p in pats:
            n = s.count(p)
            mark = "OK" if n == 0 else "!!"
            print(f"  {mark} {p!r}: {n}")
            if n:
                bad = True
                for i, line in enumerate(s.splitlines(), 1):
                    if p in line:
                        print(f"      {i}: {line.strip()[:120]}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
