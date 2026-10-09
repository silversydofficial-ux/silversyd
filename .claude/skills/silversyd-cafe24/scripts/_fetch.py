"""공용: URL 또는 로컬 파일에서 HTML 읽기."""
import os, time, urllib.request

UA_PC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
UA_MO = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


def read(src, mobile=False):
    if os.path.exists(src):
        return open(src, encoding="utf-8", errors="replace").read()
    url = src + ("&" if "?" in src else "?") + "v=%d" % time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA_MO if mobile else UA_PC})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")
