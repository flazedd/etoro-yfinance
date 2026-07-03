"""One-off: drop today's still-open session bar from the already-stored data.

Trims every native + EUR Parquet in place (removes any bar dated today-or-later,
UTC) and recomputes the coverage windows in yf_validation_cache.json so
`price_to`/`vol_to` reflect the last *closed* session. Run after pulling the
fetch-side fix; new runs already exclude the unclosed bar.

    uv run python scripts/trim_unclosed.py
    uv run python scripts/build_liquidity.py   # refresh turnover from trimmed data
"""
from __future__ import annotations

import json
from datetime import UTC, datetime

import pandas as pd

from etoro_yfinance import prices
from etoro_yfinance.web.data import data_dir


def _trim_store(eur: bool) -> int:
    today = datetime.now(UTC).date()
    trimmed = 0
    for p in prices.prices_dir(eur=eur).glob("*.parquet"):
        df = pd.read_parquet(p)
        keep = df[pd.to_datetime(df["date"]).dt.date < today]
        if len(keep) != len(df):
            keep.to_parquet(p, index=False)
            trimmed += 1
    return trimmed


def _windows(df):
    def w(mask):
        idx = df.index[mask]
        return (str(min(idx)), str(max(idx))) if len(idx) else (None, None)

    price = df["close"] if "close" in df.columns else df["adj_close"]
    pf, pt = w(price.notna().to_numpy())
    vf, vt = w(df["volume"].fillna(0).to_numpy() > 0)
    return {"price_from": pf, "price_to": pt, "vol_from": vf, "vol_to": vt,
            "bars": len(df)}


def main() -> int:
    n_native = _trim_store(eur=False)
    n_eur = _trim_store(eur=True)
    print(f"trimmed {n_native} native + {n_eur} EUR parquet files (dropped today's bar)")

    cache_path = data_dir() / "yf_validation_cache.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
        updated = 0
        for t, v in cache.items():
            if v is None:            # dead/delisted ticker — no parquet, leave as-is
                continue
            df = prices.load_prices(t)
            if df is None or df.empty:
                continue
            cache[t] = _windows(df)
            updated += 1
        cache_path.write_text(json.dumps(cache))
        print(f"recomputed coverage windows for {updated} tickers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
