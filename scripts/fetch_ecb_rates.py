"""Download the ECB euro foreign-exchange reference rates into a local table.

Source: the ECB's `eurofxref-hist.zip` — daily reference rates back to 1999 for
~30 currencies, free and stable. Written to data/ecb_rates.parquet as a
date-indexed table of CCY-per-EUR (i.e. 1 EUR = value CCY), plus an EUR column
of 1.0. Used to convert native price/volume series into euros.

    uv run python scripts/fetch_ecb_rates.py     # refresh

Caveats baked into the consumer, not here: rates are a single daily fix (~16:00
CET), weekdays only — forward-fill onto trading days when converting.
"""
from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path

URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
OUT = Path("data/ecb_rates.parquet")


def main() -> int:
    import pandas as pd

    print(f"downloading {URL}")
    raw = urllib.request.urlopen(URL, timeout=60).read()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = z.namelist()[0]
        df = pd.read_csv(io.BytesIO(z.read(name)))

    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()
    # Drop empty/all-NaN trailer columns; coerce to float.
    df = df.dropna(axis=1, how="all").apply(pd.to_numeric, errors="coerce")
    df["EUR"] = 1.0  # base currency

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT)
    print(f"wrote {OUT}: {len(df):,} days × {len(df.columns)} currencies "
          f"({df.index.min().date()} → {df.index.max().date()})")
    print("currencies:", ", ".join(sorted(df.columns)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
