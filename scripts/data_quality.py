"""Audit the price stores: what the quality filter found, fixed and rejected.

`prices.write_prices` writes a per-series report to data/quality/<ticker>.json
for every instrument it ingests, so the default run just aggregates those — no
rescan needed. `--rescan` recomputes them from the raw and clean stores, which
is what to run after changing a threshold in `prices.clean_frame`.

    uv run python scripts/data_quality.py            # summarise the store
    uv run python scripts/data_quality.py --rescan    # recompute, then summarise
    uv run python scripts/data_quality.py --rejects   # list every excluded ticker
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

from etoro_yfinance import prices


def _rescan_one(ticker: str) -> dict | None:  # type: ignore[type-arg]
    raw = prices.load_prices(ticker, raw=True)
    if raw is None or raw.empty:
        return None
    clean = prices.clean_frame(raw)
    rep = prices.quality_report(ticker, raw, clean)
    prices.write_quality(ticker, rep)
    return rep


def _load_reports(rescan: bool) -> list[dict]:  # type: ignore[type-arg]
    if rescan:
        names = [p.stem for p in sorted(prices.prices_dir(raw=True).glob("*.parquet"))]
        out = []
        workers = max(1, (os.cpu_count() or 4) - 2)
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for i, rep in enumerate(ex.map(_rescan_one, names, chunksize=32), 1):
                if rep:
                    out.append(rep)
                if i % 2000 == 0:
                    print(f"  {i}/{len(names)}", file=sys.stderr, flush=True)
        return out
    files = sorted(prices.quality_dir().glob("*.json"))
    return [json.loads(p.read_text()) for p in files]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rescan", action="store_true", help="recompute from the stores")
    ap.add_argument("--rejects", action="store_true", help="list every excluded ticker")
    a = ap.parse_args()

    reports = _load_reports(a.rescan)
    if not reports:
        print("no reports — run with --rescan (or ingest something first)")
        return 1
    d = pd.DataFrame(reports)
    n = len(d)
    admitted = d[d.admitted]
    print(f"\n{n:,} series ingested, floor {prices.MIN_DATE.date()}\n")
    print(f"  admitted to the clean store : {len(admitted):,} ({len(admitted) / n * 100:.2f}%)")
    for reason, k in Counter(d.loc[~d.admitted, "reason"]).most_common():
        print(f"  rejected — {reason!s:<12s}      : {k:,} ({k / n * 100:.2f}%)")

    print()
    for key, label in (("rows", "rows  "), ("cells", "prices")):
        raw_n = sum(r["raw"][key] for r in reports)
        clean_n = sum(r["clean"][key] for r in reports)
        print(f"  {label} {raw_n:>13,} -> {clean_n:>13,}")
    repaired = sum(
        1 for r in reports if r["admitted"] and r["clean"]["cells"] < r["raw"]["cells"]
    )
    print(f"  admitted series with at least one repaired bar: {repaired:,}")

    if "worst_move" in d.columns and admitted.worst_move.notna().any():
        w = admitted.worst_move.dropna()
        print("\n  worst single-bar move in the RAW series of admitted names:")
        for q in (50, 90, 99, 100):
            print(f"    p{q:<4} {w.quantile(q / 100) * 100:>12,.1f}%")

    if a.rejects:
        print("\nrejected:")
        for _, r in d[~d.admitted].sort_values(["reason", "ticker"]).iterrows():
            extra = f"frozen_run={r.get('frozen_run')}, median={r.get('median_price')}"
            print(f"  {r.ticker:14s} {r.reason!s:10s} {extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
