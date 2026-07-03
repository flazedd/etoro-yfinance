"""Mirror the eToro API documentation into docs/etoro/ for fast local reading.

Source: https://api-portal.etoro.com — eToro publishes an `llms.txt` index plus
per-endpoint markdown pages and machine-readable OpenAPI specs, explicitly for
programmatic/AI consumption. We keep a local copy so the docs are greppable and
readable offline (the OpenAPI spec has every endpoint/param/schema; the .md
pages carry the prose + examples).

    uv run python scripts/fetch_etoro_docs.py

Re-run any time to refresh. The portal sits behind Cloudflare, which blocks the
default urllib UA, so we send a browser User-Agent and go one request at a time.
"""
from __future__ import annotations

import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://api-portal.etoro.com"
INDEX = f"{BASE}/llms.txt"
SPECS = [
    f"{BASE}/api-reference/openapi.json",
    f"{BASE}/api-reference/deprecated-openapi.json",
]
OUT = Path("docs/etoro")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
DELAY = 0.4  # polite gap between requests (Cloudflare-friendly, sequential)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def local_path(url: str) -> Path:
    return OUT / url[len(BASE) + 1:]  # mirror the path after the host


def save(url: str, data: bytes) -> None:
    p = local_path(url)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    print(f"index: {INDEX}")
    index = fetch(INDEX)
    (OUT / "llms.txt").write_bytes(index)

    urls = SPECS + sorted(set(re.findall(r"https?://[^\s)]+\.md", index.decode("utf-8"))))
    print(f"mirroring {len(urls)} files -> {OUT}/")

    ok = 0
    failed: list[str] = []
    for i, url in enumerate(urls, 1):
        try:
            save(url, fetch(url))
            ok += 1
        except (urllib.error.URLError, OSError) as e:
            failed.append(f"{url}  ({e})")
        if i % 25 == 0 or i == len(urls):
            print(f"  {i}/{len(urls)} ({ok} ok, {len(failed)} failed)")
        time.sleep(DELAY)

    print(f"\ndone: {ok}/{len(urls)} files under {OUT}/")
    if failed:
        print(f"{len(failed)} failed:")
        for f in failed[:20]:
            print("  -", f)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
