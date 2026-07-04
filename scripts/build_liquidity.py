"""Compute per-instrument turnover liquidity from the EUR store.

For each ticker in data/prices_eur/, computes median daily €-turnover over the
last ~year (adv_eur) and the no-trade-day fraction, and writes
data/liquidity_cache.json {ticker: {adv_eur, zero_vol_frac, obs}}. Free — no
network; just reads the derived EUR series (build_eur_series.py must have run).

    uv run python scripts/build_liquidity.py
"""

from __future__ import annotations

import json

from etoro_yfinance import liquidity, prices
from etoro_yfinance.web.data import data_dir


def main() -> int:
    tickers = prices.available_tickers(eur=True)
    if not tickers:
        print("no data/prices_eur/ — run scripts/build_eur_series.py first")
        return 1

    out: dict[str, dict] = {}
    for i, t in enumerate(tickers, 1):
        df = prices.load_prices(t, eur=True)
        if df is None or "volume" not in df.columns:
            continue
        out[t] = liquidity.turnover_stats(df["volume"])
        if i % 1000 == 0:
            print(f"  {i}/{len(tickers)}")

    cache = data_dir() / "liquidity_cache.json"
    cache.write_text(json.dumps(out))
    have = [v["adv_eur"] for v in out.values() if v["adv_eur"]]
    have.sort()
    med = have[len(have) // 2] if have else 0
    print(f"wrote {cache}: {len(out)} instruments, {len(have)} with turnover")
    print(f"median adv_eur across universe: €{med:,.0f}/day")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
