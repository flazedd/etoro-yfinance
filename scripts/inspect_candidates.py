"""Inspect IBKR contract candidates for the non-resolved universe names.

For every company in data/<slug>_ibkr_resolution.json that is NOT 'resolved',
do an ISIN search (and a ticker search) and dump every STK contract IBKR offers
— conid, symbol, listing venue — so we can hand-pick a CONID_OVERRIDES pin for
the same company on a tradeable venue. Suggests one per name by venue priority.

    uv run python scripts/inspect_candidates.py --sleep 0.4

Writes data/<slug>_override_candidates.json and prints a per-name table.
Read-only against IBKR; places no orders.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect.contract_resolver import _parse_isin_row  # noqa: E402

DATA_DIR = Path("data")

# Venue-priority for the suggested pin, by the kind of instrument. The first
# venue present among a name's candidates wins.
US_PRIMARY = ["NYSE", "NASDAQ", "AMEX", "ARCA", "BATS"]
HOME_BY_PREFIX = {  # ISIN country prefix -> preferred home venues
    "HK": ["SEHK"],
    "CN": ["SEHK"],
    "JP": ["TSEJ"],
}
# Venues that are NOT real, tradeable listings — IBKR's valuation/quote-only books.
_DEAD_VENUES = {"VALUE"}


def _suggest(isin: str, name: str, contracts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Pick the best tradeable contract for the SAME company."""
    venues = {c["venue"]: c for c in contracts}
    live = {v: c for v, c in venues.items() if v not in _DEAD_VENUES}
    if not live:
        return None  # only dead/valuation venues -> delisted, exclude
    pref: list[str] = []
    if isin[:2] in HOME_BY_PREFIX:
        pref = HOME_BY_PREFIX[isin[:2]]
    elif isin[:2] == "US" or "ADR" in name.upper():
        pref = US_PRIMARY
    for v in pref:
        if v in live:
            return live[v]
    # Fall back to the single live venue, or the first one.
    return next(iter(live.values()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default="leonteq", help="resolution-file slug")
    parser.add_argument("--sleep", type=float, default=0.4, help="pause between IBKR calls")
    args = parser.parse_args()

    res_path = DATA_DIR / f"{args.slug}_ibkr_resolution.json"
    saved = json.loads(res_path.read_text())
    todo = [x for x in saved["results"].values() if x["status"] != "resolved"]
    print(f"{len(todo)} non-resolved names to inspect\n")

    from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError

    client = IBKRClient()
    out: dict[str, Any] = {}
    with client:
        for i, x in enumerate(todo, 1):
            isin = str(x.get("isin") or "").strip()
            name = str(x.get("company_name") or "")
            contracts: list[dict[str, Any]] = []
            try:
                rows = client.secdef_search_raw(isin) if isin else []
            except IBKRError as e:
                print(f"  [{i:2}] {x['ticker']:8} ERR {e}")
                rows = []
            seen = set()
            for row in rows:
                parsed = _parse_isin_row(row) if isinstance(row, dict) else None
                if not parsed:
                    continue
                conid, symbol, venue = parsed
                if (conid, venue) in seen:
                    continue
                seen.add((conid, venue))
                contracts.append({"conid": conid, "symbol": symbol, "venue": venue})
            sug = _suggest(isin, name, contracts)
            out[str(x["company_id"])] = {
                "company_id": x["company_id"], "ticker": x["ticker"],
                "exchange": x["exchange"], "currency": x["currency"], "isin": isin,
                "company_name": name, "candidates": contracts, "suggested": sug,
            }
            tag = (f"PIN {sug['conid']} {sug['symbol']}@{sug['venue']}"
                   if sug else "EXCLUDE (no live venue)")
            print(f"  [{i:2}] {x['ticker']:8} {x['exchange']:5} {name[:30]:30} -> {tag}")
            cand_str = ", ".join(f"{c['symbol']}@{c['venue']}:{c['conid']}" for c in contracts[:8])
            print(f"        candidates: {cand_str or '(none)'}")
            if args.sleep:
                time.sleep(args.sleep)

    out_path = DATA_DIR / f"{args.slug}_override_candidates.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
