"""Derive the euro-converted price/volume series for every stored instrument.

Reads the pristine native OHLCV (data/prices/), converts with the ECB reference
rates (data/ecb_rates.parquet) using each instrument's listing currency, and
writes data/prices_eur/<ticker>.parquet — prices in EUR, `volume` = EUR turnover
(equities: price×shares; crypto: USD notional). Originals are left untouched.

    uv run python scripts/fetch_ecb_rates.py      # once / to refresh FX
    uv run python scripts/build_eur_series.py     # (re)build the EUR store
"""

from __future__ import annotations

import json
from collections import Counter

from etoro_yfinance import currency, prices
from etoro_yfinance.web.data import data_dir


def main() -> int:
    ecb = prices.load_ecb_rates()
    if ecb is None:
        print("no data/ecb_rates.parquet — run scripts/fetch_ecb_rates.py first")
        return 1

    rows = json.loads((data_dir() / "etoro_universe_mapping.json").read_text())["rows"]
    status_by_yf: dict[str, str] = {}
    for r in rows:  # dedup by yfinance ticker (crypto collapses)
        yf = r.get("yf")
        if yf and yf not in status_by_yf:
            status_by_yf[yf] = r.get("status")

    ok = 0
    skipped: Counter = Counter()
    for yf, status in status_by_yf.items():
        df = prices.load_prices(yf)
        if df is None:
            continue
        ccy = currency.currency_for(yf, status)
        if not ccy:
            skipped["<no currency>"] += 1
            continue
        if prices.write_prices_eur(yf, df, ccy, status, ecb):
            ok += 1
        else:
            skipped[ccy] += 1  # currency not in ECB table

    print(f"wrote {ok} EUR series -> {prices.prices_dir(eur=True)}/")
    if skipped:
        print("skipped (unconvertible):", dict(skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
