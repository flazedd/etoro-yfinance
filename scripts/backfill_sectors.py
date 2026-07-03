"""Backfill a sector for instruments that qualify for the universe but lack one.

eToro leaves ~some stocks without an industry and many UCITS ETFs without a Yahoo
category. For those, fall back to Yahoo's own `.info['sector']` (GICS-style, e.g.
"Technology", "Financial Services"). Writes data/sector_override_cache.json
{yfinance_ticker: sector}; the mapping build + web overlay use it wherever the
primary sector is missing.

Only the sector_gap (passes every universe criterion except sector) is probed —
a small, resumable, canary-guarded sweep.

    uv run python scripts/backfill_sectors.py
"""
from __future__ import annotations

import json
import time

from etoro_yfinance import universe
from etoro_yfinance.web.data import data_dir

_CACHE = "sector_override_cache.json"
_PACE = 0.6
_CANARY = "AAPL"       # always has a sector; distinguishes throttle from genuine-none
_CANARY_AFTER = 8


def _sector(yf_client, t):
    try:
        info = yf_client.Ticker(t).info
        return info.get("sector") or info.get("category")   # stocks → sector; ETF → category
    except Exception:
        return None


def main() -> int:
    import yfinance as yf

    gap = universe.sector_gap()                 # default criteria
    tickers = sorted({r["yf"] for r in gap if r.get("yf")})

    cache_path = data_dir() / _CACHE
    cache: dict = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text())
        except Exception:
            cache = {}
    todo = [t for t in tickers if t not in cache]
    print(f"backfill-sectors: gap={len(tickers)}, {len(tickers) - len(todo)} cached, "
          f"probing {len(todo)}")

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    pending: list[str] = []
    throttled = False
    for n, t in enumerate(todo, 1):
        sec = _sector(yf, t)
        if sec:
            for p in pending:
                cache[p] = None
            pending.clear()
            cache[t] = sec
        else:
            pending.append(t)
            if len(pending) >= _CANARY_AFTER:
                if _sector(yf, _CANARY):        # Yahoo up → empties are genuine
                    for p in pending:
                        cache[p] = None
                    pending.clear()
                else:
                    print(f"  canary empty near {t} — throttled; stopping. Re-run to resume.")
                    throttled = True
                    break
        if n % 25 == 0:
            save()
            got = sum(1 for v in cache.values() if v)
            print(f"  {n}/{len(todo)} probed · {got} found", flush=True)
        time.sleep(_PACE)

    if not throttled:
        for p in pending:
            cache[p] = None
    save()
    got = sum(1 for v in cache.values() if v)
    print(f"done: {got} sectors found / {len(cache)} resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
