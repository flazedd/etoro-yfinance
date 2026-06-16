"""Verify every resolved bbterminal->IBKR conid is actually the same company.

Resolving a conid only proves we FOUND something; this proves it's the RIGHT
company, using a signal independent of how we resolved it:

  * NAME   — IBKR's own company name for the conid (via trsrv/secdef, batched)
             vs bbterminal's company_name. This is the signal that catches a
             wrong ISIN in bbterminal (it resolved cleanly, but to a different
             company — e.g. SM Energy vs SM Investments).
  * CCY    — IBKR currency vs bbterminal currency (ADR overrides legitimately
             differ, so a known override is exempt).
  * CUSIP  — for US-ISIN names, optional second pass (--cusip) compares IBKR's
             cusip to the middle of bbterminal's US ISIN: a true ISIN check.

Confidence per company:
  high    name >= --high (default 0.7) and currency ok
  medium  name >= --med  (default 0.4)
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

from ibkr_portfolio_connect.contract_resolver import CONID_OVERRIDES  # noqa: E402
from ibkr_portfolio_connect.name_match import similarity  # noqa: E402

DATA_DIR = Path("data")
_BATCH = 50  # conids per trsrv/secdef call


def _override_keys() -> set[tuple[str, str]]:
    return set(CONID_OVERRIDES.keys())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default="leonteq")
    parser.add_argument("--high", type=float, default=0.7, help="name score for 'high'")
    parser.add_argument("--med", type=float, default=0.4, help="name score for 'medium'")
    parser.add_argument("--cusip", action="store_true", help="second pass: US ISIN/CUSIP check")
    parser.add_argument("--sleep", type=float, default=0.3, help="pause between --cusip calls")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()

    res = json.loads((DATA_DIR / f"{args.slug}_ibkr_resolution.json").read_text())
    resolved = [x for x in res["results"].values()
                if x.get("status") == "resolved" and x.get("conid")]
    ver_path = DATA_DIR / f"{args.slug}_mapping_verification.json"

    if args.summary_only:
        saved = json.loads(ver_path.read_text())
        _summary(list(saved["results"].values()), args)
        return 0

    from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError

    overrides = _override_keys()
    by_conid = {int(x["conid"]): x for x in resolved}
    out: dict[str, dict[str, Any]] = {}

    client = IBKRClient()
    with client:
        # ---- pass 1: batched name + currency ------------------------------
        conids = list(by_conid)
        print(f"verifying {len(conids)} resolved conids (name + currency)\n")
        for i in range(0, len(conids), _BATCH):
            chunk = conids[i : i + _BATCH]
            try:
                defs = client.secdef_by_conids(chunk)
            except IBKRError as e:
                print(f"  batch {i // _BATCH} failed: {e}", file=sys.stderr)
                defs = []
            got = {int(d["conid"]): d for d in defs if d.get("conid") is not None}
            for cid in chunk:
                bb = by_conid[cid]
                d = got.get(cid)
                ibkr_name = str((d or {}).get("name") or "")
                ibkr_ccy = str((d or {}).get("currency") or "")
                ibkr_listing = str((d or {}).get("listingExchange") or "")
                name_score = similarity(bb.get("company_name", ""), ibkr_name) if d else 0.0
                is_override = (bb["ticker"].upper(), bb["exchange"].upper()) in overrides
                ccy_ok = is_override or not ibkr_ccy or ibkr_ccy == bb.get("currency")
                if d is None:
                    conf = "missing"
                elif name_score >= args.high and ccy_ok:
                    conf = "high"
                elif name_score >= args.med:
                    conf = "medium"
                else:
                    conf = "low"
                out[str(bb["company_id"])] = {
                    "company_id": bb["company_id"], "ticker": bb["ticker"],
                    "exchange": bb["exchange"], "conid": cid, "method": bb.get("method"),
                    "bb_name": bb.get("company_name"), "ibkr_name": ibkr_name,
                    "name_score": round(name_score, 3),
                    "bb_ccy": bb.get("currency"), "ibkr_ccy": ibkr_ccy,
                    "ccy_ok": ccy_ok, "ibkr_listing": ibkr_listing,
                    "is_override": is_override, "confidence": conf,
                }
            print(f"  [{min(i + _BATCH, len(conids)):4}/{len(conids)}] batched")

        # ---- pass 2 (optional): US ISIN/CUSIP cross-check -----------------
        if args.cusip:
            us = [r for r in out.values()
                  if str(by_conid[r["conid"]].get("isin") or "").startswith("US")]
            print(f"\nCUSIP cross-check for {len(us)} US-ISIN names ...")
            for j, r in enumerate(us, 1):
                bb_isin = str(by_conid[r["conid"]].get("isin") or "")
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
