#!/usr/bin/env python3
"""복사 버튼이 달린 찾기/바꾸기 적용 가이드(단독 HTML)를 만든다.

사용: python3 make_guide.py spec.json 출력.html
spec 예시는 assets/guide_example.json. 경로는 spec 파일 기준 상대경로.

spec 키
  number    차수 (예: 75)
  title     제목
  lead      한두 문장 요약
  sections  [{"h": "원인", "items": ["...", "..."]}, {"h": "...", "html": "<p>...</p>"}]
  steps     [{"file": "layout.html", "find": "한 줄" 또는 {"path": "f.txt"},
              "replace": "..." 또는 {"path": "r.html"}, "note": "선택"}]
            find 를 비우면 '파일 맨 아래에 붙여넣기' 단계가 된다.
  rollback  되돌리는 법 한 문장
  checked   확인한 내용 목록
바꿀 내용은 자동으로 금지 문자열 검사를 하고, 걸리면 만들지 않는다.
"""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_BAD = ["$", "?>", "</head", "</body", "http"]
TEXT_BAD = ["—", "·"]

COPY_JS = """<script>
document.querySelectorAll('.copybtn').forEach(function (b) {
  b.addEventListener('click', function () {
    var t = b.parentElement.querySelector('pre').textContent;
    var done = function () { b.textContent = '복사됨'; b.classList.add('done');
      setTimeout(function () { b.textContent = '복사'; b.classList.remove('done'); }, 1600); };
    if (navigator.clipboard && window.isSecureContext !== false) navigator.clipboard.writeText(t).then(done, fallback); else fallback();
    function fallback() { var a = document.createElement('textarea'); a.value = t; document.body.appendChild(a); a.select();
      try { document.execCommand('copy'); done(); } catch (e) {} a.remove(); }
  });
});
</script>"""


def load(v, base):
    if isinstance(v, dict):
        return open(os.path.join(base, v["path"]), encoding="utf-8").read().rstrip("\n")
    return (v or "").rstrip("\n")


def code(text, find=False):
    cls = "codewrap find" if find else "codewrap"
    return f'<div class="{cls}"><button class="copybtn">복사</button><pre>{html.escape(text)}</pre></div>'


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    spec_path, out = sys.argv[1], sys.argv[2]
    base = os.path.dirname(os.path.abspath(spec_path))
    sp = json.load(open(spec_path, encoding="utf-8"))
    css = open(os.path.join(HERE, "..", "assets", "guide.css"), encoding="utf-8").read()

    problems = []
    parts = [f'<h1>{html.escape(sp["title"])} <span class="tag">{sp["number"]}차</span></h1>']
    if sp.get("lead"):
        parts.append(f'<p class="lead">{html.escape(sp["lead"])}</p>')
    n = 0
    for s in sp.get("sections", []):
        n += 1
        parts.append(f'<h2>{n}. {html.escape(s["h"])}</h2>')
        if "html" in s:
            parts.append(s["html"])
        if s.get("items"):
            parts.append("<ul>" + "".join(f"<li>{x}</li>" for x in s["items"]) + "</ul>")
    steps = sp.get("steps", [])
    if steps:
        n += 1
        parts.append(f'<h2>{n}. 적용 <span class="tag">{len(steps)}건</span></h2>')
        for k, st in enumerate(steps, 1):
            fnd, rep = load(st.get("find"), base), load(st.get("replace"), base)
            for p in CODE_BAD:
                if p in rep:
                    problems.append(f"단계 {k} 바꿀 내용에 {p!r} {rep.count(p)}개")
            if "\n" in fnd:
                problems.append(f"단계 {k} 찾을 내용이 여러 줄 (편집기 검색은 한 줄만 찾음)")
            if any(c in fnd for c in "()[]\\"):
                problems.append(f"단계 {k} 찾을 내용에 괄호/역슬래시 (편집기 검색 실패 전례)")
            f = html.escape(st.get("file", "layout.html"))
            parts.append('<div class="step">')
            if fnd:
                parts.append(f'<p>디자인 &gt; 디자인 관리 &gt; <b>{f}</b> 에서 아래 한 줄을 찾아 두 번째 코드로 바꿔 주십시오.</p>')
                parts.append('<p class="lab">찾을 내용 (한 줄)</p>' + code(fnd, True))
                parts.append('<p class="lab">바꿀 내용</p>' + code(rep))
            else:
                parts.append(f'<p>디자인 &gt; 디자인 관리 &gt; <b>{f}</b> 파일 맨 아래에 붙여 넣어 주십시오.</p>')
                parts.append('<p class="lab">붙여 넣을 내용</p>' + code(rep))
            if st.get("note"):
                parts.append(f'<p style="font-size:13px;color:#666">{st["note"]}</p>')
            parts.append("</div>")
    if sp.get("rollback"):
        parts.append(f'<div class="box"><p style="margin:0">{sp["rollback"]}</p></div>')
    if sp.get("checked"):
        n += 1
        parts.append(f"<h2>{n}. 확인한 내용</h2><ul>" + "".join(f"<li>{x}</li>" for x in sp["checked"]) + "</ul>")

    body = "\n".join(parts)
    visible = "\n".join([sp["title"], sp.get("lead", ""), json.dumps(sp.get("sections", []), ensure_ascii=False),
                         json.dumps(sp.get("checked", []), ensure_ascii=False), sp.get("rollback", "")])
    for p in TEXT_BAD:
        if p in visible:
            problems.append(f"설명 문구에 {p!r} (가로 대시, 중간점 금지)")
    if problems:
        print("만들지 않음:"); [print(" -", x) for x in problems]; sys.exit(1)

    doc = ("<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n"
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
           f"<title>실버시드 {sp['number']}차 - {html.escape(sp['title'])}</title>\n<style>\n{css}</style>\n</head>\n<body>\n"
           f"<div class=\"wrap\">\n{body}\n</div>\n{COPY_JS}\n" + "</" + "body>\n</html>\n")
    open(out, "w", encoding="utf-8").write(doc)
    print("만듦:", out)


if __name__ == "__main__":
    main()
