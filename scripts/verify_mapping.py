"""Verify every resolved bbterminal->IBKR conid is actually the same company.

Resolving a conid only proves we FOUND something; this proves it's the RIGHT
company, using a signal independent of how we resolved it:

  * NAME   — IBKR's own company name for the conid (via trsrv/secdef, batched)
             vs bbterminal's company_name. This is the signal that catches a
             wrong ISIN in bbterminal (it resolved cleanly, but to a different
             company — e.g. SM Energy vs SM Investments).
  * TICKER — IBKR's symbol for the conid vs bbterminal's ticker (HK-style zero
             padding ignored). An independent identity signal: a matching ticker
             on the resolved (ISIN-first, expected-exchange) listing confirms the
             company even when the display NAMES differ (rebrands, ADR labels).
  * CCY    — IBKR currency vs bbterminal currency (ADR overrides legitimately
             differ, so a known override is exempt).
  * CUSIP  — for US-ISIN names, optional second pass (--cusip) compares IBKR's
             cusip to the middle of bbterminal's US ISIN: a true ISIN check.

Confidence per company (NAME *or* TICKER confirms identity):
  high    (name >= --high OR ticker matches) and currency ok
  medium  name >= --med, or ticker matches but currency differs
  low     below that — REVIEW (possible wrong mapping)

    uv run python scripts/verify_mapping.py                 # name+ccy sweep (batched, fast)
    uv run python scripts/verify_mapping.py --cusip --sleep 0.3   # + per-conid CUSIP check
    uv run python scripts/verify_mapping.py --summary-only

Writes data/<slug>_mapping_verification.json. Read-only; no orders.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect.contract_resolver import (  # noqa: E402
    BBTERMINAL_TO_IBKR_LISTING,
    CONID_OVERRIDES,
)
from ibkr_portfolio_connect.name_match import similarity  # noqa: E402

DATA_DIR = Path("data")
_BATCH = 50  # conids per trsrv/secdef call


def _override_keys() -> set[tuple[str, str]]:
    return set(CONID_OVERRIDES.keys())


def _norm_ticker(t: str) -> str:
    """Loose ticker compare: drop case, spaces, dots, and leading zeros on the
    numeric HK-style codes so bbterminal '00189' == IBKR '189'."""
    t = (t or "").upper().replace(" ", "").replace(".", "")
    return (t.lstrip("0") or "0") if t.isdigit() else t


def _load_records(slug: str, source: str) -> list[dict[str, Any]]:
    """Normalize a resolution source into the common shape this script verifies.

    ``snapshot`` — the live ``mapping_snapshot.json`` the app trades off, which
    carries EVERY resolved conid (equities + ETFs). ``resolution`` — the legacy
    offline ``<slug>_ibkr_resolution.json`` artifact (can be partial/stale)."""
    if source == "snapshot":
        data = json.loads((DATA_DIR / "mapping_snapshot.json").read_text())
        raw = [r for r in data.get("rows", []) if r.get("conid")]
        name_key = "name"
    else:
        data = json.loads((DATA_DIR / f"{slug}_ibkr_resolution.json").read_text())
        raw = [x for x in data["results"].values()
               if x.get("status") == "resolved" and x.get("conid")]
        name_key = "company_name"
    out: list[dict[str, Any]] = []
    for r in raw:
        out.append({
            "company_id": r.get("company_id"),
            "company_name": r.get(name_key) or "",
            "ticker": str(r.get("ticker") or ""),
            "exchange": str(r.get("exchange") or ""),
            "currency": r.get("currency"),
            "conid": int(r["conid"]),
            "method": r.get("method"),
            "ibkr_symbol": str(r.get("ibkr_symbol") or ""),
            "isin": str(r.get("isin") or ""),
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default="leonteq")
    parser.add_argument("--source", choices=("snapshot", "resolution"), default="snapshot",
                        help="verify the live mapping_snapshot.json (default, full universe) "
                             "or the legacy <slug>_ibkr_resolution.json artifact")
    parser.add_argument("--high", type=float, default=0.7, help="name score for 'high'")
    parser.add_argument("--med", type=float, default=0.4, help="name score for 'medium'")
    parser.add_argument("--cusip", action="store_true", help="second pass: US ISIN/CUSIP check")
    parser.add_argument("--sleep", type=float, default=0.3, help="pause between --cusip calls")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    records = _load_records(args.slug, args.source)
    by_cid = {str(r["company_id"]): r for r in records}
    ver_path = DATA_DIR / f"{args.slug}_mapping_verification.json"

    if args.summary_only:
        saved = json.loads(ver_path.read_text())
        _summary(list(saved["results"].values()), args)
        return 0

    from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError

    overrides = _override_keys()
    out: dict[str, dict[str, Any]] = {}

    client = IBKRClient()
    with client:
        # ---- pass 1: batched name + currency ------------------------------
        # Fetch names once per unique conid, then score every record — two
        # companies can legitimately share a conid (e.g. an ADR override), so we
        # iterate records, not conids, or the second one would go unscored.
        conids = sorted({r["conid"] for r in records})
        print(f"verifying {len(records)} records / {len(conids)} conids (name + currency)\n")
        name_by_conid: dict[int, dict[str, Any]] = {}
        for i in range(0, len(conids), _BATCH):
            chunk = conids[i : i + _BATCH]
            try:
                defs = client.secdef_by_conids(chunk)
            except IBKRError as e:
                print(f"  batch {i // _BATCH} failed: {e}", file=sys.stderr)
                defs = []
            for d in defs:
                if d.get("conid") is not None:
                    name_by_conid[int(d["conid"])] = d
            print(f"  [{min(i + _BATCH, len(conids)):4}/{len(conids)}] batched")

        for bb in records:
            d = name_by_conid.get(bb["conid"])
            ibkr_name = str((d or {}).get("name") or "")
            ibkr_ccy = str((d or {}).get("currency") or "")
            ibkr_listing = str((d or {}).get("listingExchange") or "")
            name_score = similarity(bb["company_name"], ibkr_name) if d else 0.0
            is_override = (bb["ticker"].upper(), bb["exchange"].upper()) in overrides
            ccy_ok = is_override or not ibkr_ccy or ibkr_ccy == bb.get("currency")

            # Independent ticker + exchange identity check (from the resolve
            # phase, no extra IBKR call). A matching ticker confirms the
            # company even when the names disagree.
            ibkr_symbol = bb["ibkr_symbol"]
            ticker_match = bool(
                ibkr_symbol
                and _norm_ticker(bb["ticker"]) == _norm_ticker(ibkr_symbol)
            )
            expected = BBTERMINAL_TO_IBKR_LISTING.get(bb["exchange"].upper())
            listing_match = (
                None if (not ibkr_listing or expected is None)
                else ibkr_listing in expected
            )

            name_ok = name_score >= args.high
            if d is None:
                conf = "missing"
            elif (name_ok or ticker_match) and ccy_ok:
                conf = "high"
            elif name_score >= args.med or ticker_match:
                conf = "medium"
            else:
                conf = "low"
            out[str(bb["company_id"])] = {
                "company_id": bb["company_id"], "ticker": bb["ticker"],
                "exchange": bb["exchange"], "conid": bb["conid"], "method": bb.get("method"),
                "bb_name": bb["company_name"], "ibkr_name": ibkr_name,
                "name_score": round(name_score, 3),
                "ibkr_symbol": ibkr_symbol, "ticker_match": ticker_match,
                "listing_match": listing_match,
                "bb_ccy": bb.get("currency"), "ibkr_ccy": ibkr_ccy,
                "ccy_ok": ccy_ok, "ibkr_listing": ibkr_listing,
                "is_override": is_override, "confidence": conf,
            }

        # ---- pass 2 (optional): US ISIN/CUSIP cross-check -----------------
        if args.cusip:
            us = [r for r in out.values()
                  if by_cid[str(r["company_id"])]["isin"].startswith("US")]
            print(f"\nCUSIP cross-check for {len(us)} US-ISIN names ...")
            for j, r in enumerate(us, 1):
                bb_isin = by_cid[str(r["company_id"])]["isin"]
                bb_cusip = bb_isin[2:11]  # US + 9-char CUSIP + check digit
                try:
                    info = client.contract_info(r["conid"])
                except IBKRError as e:
                    r["cusip_check"] = f"error: {str(e)[:60]}"
                    continue
                ibkr_cusip = str(info.get("cusip") or "")
                r["bb_cusip"] = bb_cusip
                r["ibkr_cusip"] = ibkr_cusip
                if not ibkr_cusip:
                    r["cusip_check"] = "no_ibkr_cusip"
                elif ibkr_cusip == bb_cusip:
                    r["cusip_check"] = "match"
                else:
                    r["cusip_check"] = "MISMATCH"
                    if r["confidence"] == "high":
                        r["confidence"] = "medium"  # demote on ISIN disagreement
                if j % 25 == 0:
                    print(f"  [{j:4}/{len(us)}]")
                if args.sleep:
                    time.sleep(args.sleep)

    ver_path.write_text(json.dumps(
        {"slug": args.slug, "thresholds": {"high": args.high, "med": args.med},
         "results": out}, indent=2))
    print(f"\nwrote {ver_path}")
    _summary(list(out.values()), args)
    return 0


def _summary(rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    conf = Counter(r["confidence"] for r in rows)
    print(f"\n=== confidence ({len(rows)} resolved) ===")
    for k in ("high", "medium", "low", "missing"):
        if conf.get(k):
            print(f"  {k:8} {conf[k]:5}")
    cc = Counter(r.get("cusip_check") for r in rows if r.get("cusip_check"))
    if cc:
        print("  CUSIP:", dict(cc))
    flagged = sorted([r for r in rows if r["confidence"] in ("low", "medium", "missing")],
                     key=lambda r: r["name_score"])
    if flagged:
        print(f"\n=== {len(flagged)} to review (lowest name-score first) ===")
        for r in flagged:
            extra = ""
            if r.get("cusip_check") and r["cusip_check"] != "match":
                extra = f"  cusip={r['cusip_check']}"
            if not r["ccy_ok"]:
                extra += f"  ccy {r['bb_ccy']}!={r['ibkr_ccy']}"
            print(f"  {r['confidence']:6} {r['name_score']:.2f} {r['ticker']:8} {r['exchange']:5} "
                  f"conid={r['conid']:>10} [{r.get('method')}]{extra}")
            print(f"         bb='{r['bb_name']}'  ibkr='{r['ibkr_name']}'")


if __name__ == "__main__":
    sys.exit(main())
