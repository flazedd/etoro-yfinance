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
_PACE = 0.6  # seconds between requests
_CANARY = "SPY"  # known-categorized ETF to tell throttle from no-category
_CANARY_AFTER = 8  # empties-in-a-row => canary-check (throttle vs genuine None)


def _category(yf, t):
    """The Yahoo fund category for a ticker, or None (many UCITS ETFs have none)."""
    try:
        return yf.Ticker(t).info.get("category")
    except Exception:
        return None


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

    def save() -> None:
        cache_path.write_text(json.dumps(cache))

    # `pending` holds empties awaiting confirmation they're genuine (a real
    # category later, or a live canary) rather than throttle victims — so a
    # throttle is never cached as None (those retry on the next run).
    pending: list[str] = []
    throttled = False
    for n, t in enumerate(todo, 1):
        cat = _category(yf, t)
        if cat:
            for p in pending:
                cache[p] = None  # genuine no-category (Yahoo is responding)
            pending.clear()
            cache[t] = cat
        else:
            pending.append(t)
            if len(pending) >= _CANARY_AFTER:
                if _category(yf, _CANARY):  # Yahoo up → empties are genuine
                    for p in pending:
                        cache[p] = None
                    pending.clear()
                else:  # canary empty → throttled
                    print(
                        f"  canary empty near {t} — throttled; stopping "
                        f"({len(pending)} unconfirmed not cached). Re-run to resume."
                    )
                    throttled = True
                    break
        if n % 50 == 0:
            save()
            got = sum(1 for v in cache.values() if v)
            print(f"  {n}/{len(todo)} probed · {got} categorized", flush=True)
        time.sleep(_PACE)

    if not throttled:  # loop finished cleanly → trailing empties genuine
        for p in pending:
            cache[p] = None
    save()
    got = sum(1 for v in cache.values() if v)
    print(f"done: {got} categorized / {len(cache)} resolved ({len(etfs) - len(cache)} left)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
