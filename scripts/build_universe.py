"""Snapshot a backtestable, executable eToro universe to data/universe_<name>.json.

Each instrument row carries both the eToro instrument_id (for execution) and the
yfinance ticker (for analysis), plus sector / liquidity / spread / history so the
backtest can size, cost, and slice without another lookup.

    uv run python scripts/build_universe.py                       # defaults
    uv run python scripts/build_universe.py --min-adv 5e6 --min-bars 500
    uv run python scripts/build_universe.py --name liquid --max-spread 0.5
"""
from __future__ import annotations

import argparse

from etoro_yfinance import universe
from etoro_yfinance.web.data import load_etoro_universe


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a backtest universe snapshot.")
    ap.add_argument("--name", default="backtest")
    ap.add_argument("--min-adv", type=float, default=1_000_000.0, help="min €/day turnover")
    ap.add_argument("--min-bars", type=int, default=252, help="min daily bars (history)")
    ap.add_argument("--recent-days", type=int, default=7, help="max staleness of price_to")
    ap.add_argument("--max-spread", type=float, default=None, help="max spread %% (optional)")
    ap.add_argument("--no-require-sector", action="store_true", help="allow missing sector")
    args = ap.parse_args()

    rows = load_etoro_universe().get("rows", [])
    crit = {"min_adv": args.min_adv, "min_bars": args.min_bars,
            "recent_days": args.recent_days, "max_spread": args.max_spread}
    doc = universe.save(args.name, rows=rows, require_sector=not args.no_require_sector, **crit)
    gap = universe.sector_gap(rows=rows, **crit)

    print(f"wrote data/universe_{doc['name']}.json")
    print(f"  {doc['count']} instruments")
    print("  by sector:", doc["by_sector"])
    print(f"  sector gap (pass all but sector): {len(gap)} "
          f"— run scripts/backfill_sectors.py to fill, then rebuild")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
