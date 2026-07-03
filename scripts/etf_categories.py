"""Fetch each ETF's Morningstar-style fund category from Yahoo.

eToro's stock-sector field is meaningless for funds (a gold ETF lands in
"Financial"), so ETFs get their real classification from Yahoo's `category`
(e.g. "Commodities Focused", "Equity Energy", "Intermediate Core Bond"). Only
~1.2k ETFs, so this is a small, resumable sweep -> data/etf_category_cache.json
{yfinance_ticker: category}.

    uv run python scripts/etf_categories.py       # run / resume
"""
from __future__ import annotations

import json
import time

from etoro_yfinance.web.data import data_dir

_CACHE = "etf_category_cache.json"
_PACE = 0.6                # seconds between requests
_STOP_AFTER_EMPTY = 20     # consecutive failures => assume throttled; stop (resume later)


def main() -> int:
    import yfinance as yf

    rows = json.loads((data_dir() / "etoro_universe_mapping.json").read_text())["rows"]
    etfs = sorted({r["yf"] for r in rows if r.get("type") == "ETF" and r.get("yf")})

    cache_path = data_dir() / _CACHE
    cache: dict = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}
    todo = [t for t in etfs if t not in cache]
    print(f"etf-category: {len(etfs) - len(todo)}/{len(etfs)} cached, probing {len(todo)}")

    empty_streak = 0
    for n, t in enumerate(todo, 1):
        cat = None
        try:
            cat = yf.Ticker(t).info.get("category")
        except Exception:
            cat = None
        if cat:
            empty_streak = 0
            cache[t] = cat
        else:
            empty_streak += 1
            cache[t] = None      # recognised-but-no-category, or missing
            if empty_streak >= _STOP_AFTER_EMPTY:
                print(f"  {empty_streak} empty in a row at {t} — likely throttled; "
                      f"stopping. Re-run to resume.")
                break
        if n % 50 == 0:
            cache_path.write_text(json.dumps(cache))
            got = sum(1 for v in cache.values() if v)
            print(f"  {n}/{len(todo)} probed · {got} categorized")
        time.sleep(_PACE)

    cache_path.write_text(json.dumps(cache))
    got = sum(1 for v in cache.values() if v)
    print(f"done: {got}/{len(cache)} ETFs categorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
