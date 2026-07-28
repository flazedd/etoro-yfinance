"""Rebuild the clean price store from the raw one.

`prices.write_prices` fills both stores at ingestion, so this is only needed
after the quality filter changes: re-tune a threshold in `prices.clean_frame`,
re-run this, and the clean store is regenerated without touching the network.
The raw store is never modified.

    uv run python scripts/clean_store.py              # dry run: report only
    uv run python scripts/clean_store.py --apply      # rebuild data/prices/

Rebuild the euro store afterwards (it is derived from the clean one):

    uv run python scripts/build_eur_series.py
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor

from etoro_yfinance import prices

_APPLY = False


def _process(ticker: str) -> tuple[int, int, int, int]:
    """(rows_raw, rows_clean, cells_raw, cells_clean) for one ticker."""
    raw = prices.load_prices(ticker, raw=True)
    if raw is None or raw.empty:
        return 0, 0, 0, 0
    cols = [c for c in prices._PRICE_COLS if c in raw.columns]
    out = prices.clean_frame(raw)
    n_out = len(out)
    cells_out = int(out[cols].notna().sum().sum()) if n_out else 0
    if _APPLY:
        name = prices._safe_name(ticker)
        dest = prices.prices_dir() / f"{name}.parquet"
        if n_out == 0:
            # rejected: drop it from the clean store *and* the euro store, which
            # is derived from it and would otherwise keep a stale file
            dest.unlink(missing_ok=True)
            (prices.prices_dir(eur=True) / f"{name}.parquet").unlink(missing_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            out.reset_index().to_parquet(dest, index=False)
        prices.write_quality(ticker, prices.quality_report(ticker, raw, out))
    return len(raw), n_out, int(raw[cols].notna().sum().sum()), cells_out


def _init(apply_: bool) -> None:
    global _APPLY
    _APPLY = apply_


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write data/prices/ (default: dry run)")
    a = ap.parse_args()

    src = prices.prices_dir(raw=True)
    if not src.exists():
        print(f"no raw store at {src} — nothing to rebuild from")
        return 1
    tickers = [p.stem for p in sorted(src.glob("*.parquet"))]
    if not tickers:
        print(f"{src}: no files")
        return 1

    br = cr = bc = cc = 0
    dropped = shrunk = 0
    workers = max(1, (os.cpu_count() or 4) - 2)
    with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(a.apply,)) as ex:
        for i, (r_raw, r_out, c_raw, c_out) in enumerate(ex.map(_process, tickers, chunksize=32), 1):
            br, cr, bc, cc = br + r_raw, cr + r_out, bc + c_raw, cc + c_out
            dropped += r_out == 0
            shrunk += c_out < c_raw
            if i % 2000 == 0:
                print(f"  {i}/{len(tickers)}", file=sys.stderr, flush=True)

    verb = "rebuilt" if a.apply else "would rebuild"
    print(f"\n{prices.prices_dir()}  ({len(tickers)} tickers, {verb} from {src})")
    print(f"  rows   {br:>12,} -> {cr:>12,}   ({(br - cr) / max(br, 1) * 100:5.2f}% removed)")
    print(f"  prices {bc:>12,} -> {cc:>12,}   ({(bc - cc) / max(bc, 1) * 100:5.2f}% nulled or repaired)")
    print(f"  {shrunk} tickers lost at least one price cell; {dropped} kept nothing")
    if not a.apply:
        print("\ndry run — nothing written. Re-run with --apply.")
    else:
        print("\nnow rebuild the euro store:  uv run python scripts/build_eur_series.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
