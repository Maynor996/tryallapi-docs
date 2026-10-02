#!/usr/bin/env python3
"""把有变化的页面提交到 IndexNow（Bing / Yandex / Seznam 等共享）。

用法（域名 https://docs.tryallapi.com 上线、key 文件可访问后再运行）：
  python3 ping.py                 # 提交 lastmod 等于今天的 URL（即本次构建有变化的页面）
  python3 ping.py --since 2026-10-01
  python3 ping.py --all           # 提交 sitemap 里的全部 URL
  python3 ping.py URL [URL ...]   # 提交指定 URL
  加 --dry-run 只打印不提交
"""
import json, sys, urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import SITE_URL, INDEXNOW_KEY, DATA  # noqa: E402

ENDPOINT = "https://api.indexnow.org/indexnow"


def main(argv):
    dry = "--dry-run" in argv
    args = [a for a in argv if a != "--dry-run"]
    urls_map = json.loads((DATA / "urls.json").read_text())
    if "--all" in args:
        urls = list(urls_map)
    elif "--since" in args:
        since = args[args.index("--since") + 1]
        urls = [u for u, d in urls_map.items() if d >= since]
    elif args:
        urls = args
    else:
        today = date.today().isoformat()
        urls = [u for u, d in urls_map.items() if d == today]
    urls = [u for u in urls if u.startswith(SITE_URL)]
    if not urls:
        print("没有需要提交的 URL")
        return 0
    host = urlsplit(SITE_URL).netloc
    payload = {"host": host, "key": INDEXNOW_KEY, "keyLocation": f"{SITE_URL}/{INDEXNOW_KEY}.txt", "urlList": urls}
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    if dry:
        return 0
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("IndexNow 返回", r.status)   # 200/202 = 已接收
            return 0
    except urllib.error.HTTPError as ex:
        print("IndexNow 返回", ex.code, ex.read()[:300])
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
