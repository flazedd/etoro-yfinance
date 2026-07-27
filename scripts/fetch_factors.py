#!/usr/bin/env python
"""Ingest the covariance model's factor proxies into the local price store.

The factor set (etoro_yfinance.covariance.FACTORS) is a handful of tradable
ETFs whose daily returns *are* the factor returns. Most are already in
data/prices/ because they sit in the eToro universe, but the set is config —
a factor may point at a ticker nobody trades. This script fetches whatever is
missing (or --all to refresh everything) with the same full-history,
corporate-actions request the universe validation pass uses, and derives the
EUR series the model reads.

    uv run python scripts/fetch_factors.py            # only the missing ones
    uv run python scripts/fetch_factors.py --all      # refresh every factor
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from etoro_yfinance import covariance, currency, prices


def fetch(ticker: str) -> tuple[int, int]:
    """Download one ticker's full history and persist native + EUR. Returns
    (native rows, EUR rows); (0, 0) when the download comes back empty."""
    import pandas as pd
    import yfinance as yf

    f = yf.download(
        ticker,
        period="max",
        interval="1d",
        progress=False,
        threads=False,
        auto_adjust=False,
        actions=True,
    )
    if f is None or len(f) == 0:
        return 0, 0
    if isinstance(f.columns, pd.MultiIndex):  # single-ticker frames vary by version
        f = f.copy()
        f.columns = f.columns.get_level_values(0)
    f = f.loc[:, ~f.columns.duplicated()]
    f = prices.drop_unclosed(f)  # today's session is still moving
    if len(f) == 0:
        return 0, 0

    n = prices.write_prices(ticker, f)
    stored = prices.load_prices(ticker)
    ccy = currency.currency_for(ticker, None) or "USD"
    n_eur = prices.write_prices_eur(ticker, stored, ccy, "", prices.load_ecb_rates())
    return n, n_eur


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="refetch every factor, not just missing")
    args = ap.parse_args()

    have = set(prices.available_tickers())
    have_eur = set(prices.available_tickers(eur=True))
    rc = 0
    for name, ticker in covariance.FACTORS.items():
        if not args.all and ticker in have and ticker in have_eur:
            print(f"  {name:<11} {ticker:<6} ok (stored)")
            continue
        n, n_eur = fetch(ticker)
        if n == 0:
            print(f"  {name:<11} {ticker:<6} FAILED — empty download")
            rc = 1
        else:
            print(f"  {name:<11} {ticker:<6} {n} bars, {n_eur} EUR bars")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
