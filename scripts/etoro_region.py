"""Add a listing `region` to every row of an eToro universe JSON.

Region is derived purely from each row's listing `exchange` (already present) —
no network, no lookups. It describes WHERE THE INSTRUMENT TRADES, not where the
company is domiciled or (for ETFs) where the fund invests.

Not applicable (region = null):
  - Crypto (traded on "Digital Currency" — borderless, no listing region).
  - eToro internal/synthetic instruments (ETORIAN…, CopyPortfolios; status
    "internal") — not real exchange-listed securities.

    uv run python scripts/etoro_region.py            # annotate the mapping file
    uv run python scripts/etoro_region.py --target data/universe_backtest.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from etoro_yfinance.web.data import data_dir

# eToro exchange name -> broad listing region.
_EXCH_REGION = {
    # North America
    "Nasdaq": "North America", "NYSE": "North America",
    "OTC Markets Stock Exchange": "North America",
    "Chicago Board Options Exchange": "North America",
    "Regular Trading Hours - RTH": "North America",  # eToro RTH dupes of US large-caps
    "Toronto Stock Exchange": "North America", "TSX Venture Exchange": "North America",
    # Europe
    "LSE": "Europe", "LSE_AIM": "Europe", "LSE AIM Auction": "Europe", "LSE Auction": "Europe",
    "FRA": "Europe", "Xetra ETFs": "Europe",
    "Euronext Paris": "Europe", "Euronext Amsterdam": "Europe", "Euronext Brussels": "Europe",
    "Euronext Lisbon": "Europe",
    "Stockholm  Stock Exchange": "Europe", "Oslo Stock Exchange": "Europe",
    "Copenhagen Stock Exchange": "Europe", "Helsinki Stock Exchange": "Europe",
    "Borsa Italiana": "Europe", "Bolsa De Madrid": "Europe", "SIX": "Europe",
    "Vienna": "Europe", "Dublin EN": "Europe", "Prague SE": "Europe",
    "Warsaw": "Europe", "Budapest": "Europe",
    "Nasdaq Iceland": "Europe", "Nasdaq Tallinn": "Europe",
    "Nasdaq Vilnius": "Europe", "Nasdaq Riga": "Europe",
    # Asia-Pacific
    "Tokyo Stock Exchange": "Asia-Pacific", "TYO": "Asia-Pacific",
    "Hong Kong Exchanges": "Asia-Pacific", "Sydney": "Asia-Pacific",
    "Shenzen Stock Exchange": "Asia-Pacific", "Shanghai Stock Exchange": "Asia-Pacific",
    "National Stock Exchange of India": "Asia-Pacific", "Singapore Exchange": "Asia-Pacific",
    "Korea Exchange": "Asia-Pacific", "Taiwan Stock Exchange": "Asia-Pacific",
    # Middle East
    "Tadawul": "Middle East", "Dubai Financial Market": "Middle East",
    "Abu Dhabi": "Middle East",
}


def region_for(row: dict) -> str | None:
    """Listing region, or None when not applicable."""
    if row.get("type") == "Crypto" or row.get("exchange") == "Digital Currency":
        return None  # borderless
    if row.get("status") == "internal":
        return None  # eToro synthetic instrument, not a listed security
    return _EXCH_REGION.get(row.get("exchange") or "")


def _load_rows(target: Path) -> tuple[dict | list, list[dict]]:
    doc = json.loads(target.read_text())
    if isinstance(doc, dict) and "rows" in doc:
        return doc, doc["rows"]
    if isinstance(doc, dict) and "instruments" in doc:
        return doc, doc["instruments"]
    return doc, doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", default=None, help="universe JSON (default: mapping file)")
    args = ap.parse_args()

    target = (
        data_dir() / "etoro_universe_mapping.json" if args.target is None else Path(args.target)
    )
    doc, rows = _load_rows(target)

    dist: Counter = Counter()
    unmapped: Counter = Counter()
    for r in rows:
        reg = region_for(r)
        r["region"] = reg
        dist[reg or "(not applicable)"] += 1
        if reg is None and r.get("type") not in ("Crypto",) and r.get("status") != "internal":
            unmapped[r.get("exchange")] += 1

    target.write_text(json.dumps(doc, indent=1))
    print(f"annotated {len(rows)} rows in {target}\n")
    for reg, n in dist.most_common():
        print(f"  {n:6}  {reg}")
    if unmapped:  # a real exchange with no region entry — extend _EXCH_REGION
        print("\n  WARNING: unmapped exchanges (not crypto/internal):")
        for ex, n in unmapped.most_common():
            print(f"    {n:6}  {ex}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
