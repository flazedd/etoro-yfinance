"""Third-source ISIN verification via OpenFIGI (Bloomberg's free mapping API).

For each mapping we ask OpenFIGI "what company/ticker does this ISIN belong to?"
— an arbiter independent of both bbterminal and IBKR. Comparing all three names
turns a low name-match score into a real verdict:

  triple_match        bbterminal == IBKR == OpenFIGI  -> rock solid
  isin_identity_ok    IBKR == OpenFIGI (the ISIN's security is confirmed) and
                      bbterminal's TICKER agrees, but its NAME differs -> a
                      rename/relabel (GE->GE Aerospace) OR a bbterminal mislabel
                      (Shimano name on Sumitomo's ISIN). The security identity is
                      nailed down by 3 sources; only bbterminal's name disagrees.
  ticker_conflict     IBKR == OpenFIGI but bbterminal's name AND ticker disagree
  ibkr_figi_mismatch  OpenFIGI says the ISIN is a DIFFERENT company than our conid
                      -> our resolution may be wrong; investigate
  no_figi             OpenFIGI has no record for this ISIN

    uv run python scripts/openfigi_check.py            # flagged (low+medium) only
    uv run python scripts/openfigi_check.py --all      # every resolved mapping

No API key needed (free tier: 25 req/min x 10 ISINs). Writes
data/<slug>_openfigi.json. Read-only; no orders.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import requests

from ibkr_portfolio_connect.name_match import similarity

DATA_DIR = Path("data")
_URL = "https://api.openfigi.com/v3/mapping"
_BATCH = 10          # max jobs/request without an API key
_PER_MIN_SLEEP = 2.6  # stay under the 25 req/min unauthenticated cap
_HI = 0.6            # name-similarity "agree" threshold


def _norm_ticker(t: str) -> str:
    t = (t or "").upper().replace(" ", "").replace(".", "")
    return t.lstrip("0") or "0" if t.isdigit() else t


def _verdict(bb_name: str, ibkr_name: str, figi_name: str | None,
             bb_ticker: str, figi_tickers: set[str], method: str = "isin") -> dict[str, Any]:
    if not figi_name:
        return {"verdict": "no_figi", "sim_bb": None, "sim_ibkr": None, "ticker_match": None}
    sim_bb = round(similarity(figi_name, bb_name), 3)
    sim_ibkr = round(similarity(figi_name, ibkr_name), 3)
    tmatch = _norm_ticker(bb_ticker) in {_norm_ticker(t) for t in figi_tickers}
    # An override deliberately substitutes a different listing (e.g. TSMC's local
    # ticker 2330 -> the TSM ADR), so its ticker is *expected* to differ.
    is_override = method == "override"
    ibkr_ok, bb_ok = sim_ibkr >= _HI, sim_bb >= _HI
    if ibkr_ok and (bb_ok or tmatch or is_override):
        v = "triple_match"                # name agrees on the ISIN side; ticker/name confirm
    elif ibkr_ok or tmatch or is_override:
        v = "isin_identity_ok"            # ISIN's security confirmed (one name or the ticker); other name differs
    elif bb_ok:
        v = "ticker_conflict"             # bb name matches the ISIN but IBKR's conid name + ticker don't — investigate
    else:
        v = "ibkr_figi_mismatch"          # nothing confirms our conid is this ISIN's security
    return {"verdict": v, "sim_bb": sim_bb, "sim_ibkr": sim_ibkr, "ticker_match": tmatch}


def _map_batch(isins: list[str]) -> dict[str, list[dict[str, Any]]]:
    """ISIN -> list of OpenFIGI records (each with name/ticker/exchCode)."""
    jobs = [{"idType": "ID_ISIN", "idValue": i} for i in isins]
    r = requests.post(_URL, json=jobs, headers={"Content-Type": "application/json"}, timeout=30)
    if r.status_code == 429:
        time.sleep(8)
        r = requests.post(_URL, json=jobs, headers={"Content-Type": "application/json"}, timeout=30)
    r.raise_for_status()
    out: dict[str, list[dict[str, Any]]] = {}
    for isin, res in zip(isins, r.json(), strict=False):
        out[isin] = res.get("data") or []
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default="leonteq")
    parser.add_argument("--all", action="store_true", help="check every resolved mapping (slow)")
    parser.add_argument("--refresh", action="store_true", help="ignore cache")
    args = parser.parse_args()

    res = json.loads((DATA_DIR / f"{args.slug}_ibkr_resolution.json").read_text())["results"]
    ver = json.loads((DATA_DIR / f"{args.slug}_mapping_verification.json").read_text())["results"]

    targets = []
    for cid, r in res.items():
        if r.get("status") != "resolved" or not r.get("isin"):
            continue
        conf = ver.get(cid, {}).get("confidence")
        if args.all or conf in ("low", "medium"):
            targets.append((cid, r))

    out_path = DATA_DIR / f"{args.slug}_openfigi.json"
    out = {} if args.refresh or not out_path.exists() else json.loads(out_path.read_text()).get("results", {})
    todo = [(cid, r) for cid, r in targets if cid not in out]
    print(f"{len(targets)} targets ({'all' if args.all else 'low+medium'}); {len(todo)} to query via OpenFIGI\n")

    # Query Bloomberg only for ISINs we don't have FIGI records for yet.
    for i in range(0, len(todo), _BATCH):
        chunk = todo[i : i + _BATCH]
        isins = [r["isin"] for _, r in chunk]
        try:
            mapped = _map_batch(isins)
        except requests.HTTPError as e:
            print(f"  batch {i // _BATCH} failed: {e}", file=sys.stderr)
            mapped = {}
        for cid, r in chunk:
            recs = mapped.get(r["isin"], [])
            out[cid] = {
                "company_id": cid, "ticker": r.get("ticker"), "isin": r.get("isin"),
                "figi_name": recs[0].get("name") if recs else None,
                "figi_tickers": sorted({str(d.get("ticker")) for d in recs if d.get("ticker")}),
                "figi_exch": sorted({str(d.get("exchCode")) for d in recs if d.get("exchCode")})[:6],
            }
        out_path.write_text(json.dumps({"slug": args.slug, "results": out}, indent=2, ensure_ascii=False))
        print(f"  [{min(i + _BATCH, len(todo)):4}/{len(todo)}] queried")
        time.sleep(_PER_MIN_SLEEP)

    # Always (re)compute the verdict for EVERY target from cached FIGI records +
    # the CURRENT verification — so a matcher/threshold change is reflected on a
    # re-run without re-querying Bloomberg.
    res_by_cid = dict(targets)
    for cid in list(out):
        o = out[cid]
        r = res_by_cid.get(cid, {})
        v = ver.get(cid, {})
        o["bb_name"] = r.get("company_name", o.get("bb_name"))
        o["ibkr_name"] = v.get("ibkr_name", o.get("ibkr_name"))
        o.update(_verdict(
            o["bb_name"] or "", o["ibkr_name"] or "", o.get("figi_name"),
            o.get("ticker", ""), set(o.get("figi_tickers", [])),
            method=r.get("method", "isin"),
        ))
    out_path.write_text(json.dumps({"slug": args.slug, "results": out}, indent=2, ensure_ascii=False))

    print(f"\nwrote {out_path}")
    _summary(out)
    return 0


def _summary(out: dict[str, Any]) -> None:
    from collections import Counter
    c = Counter(v["verdict"] for v in out.values())
    print("\n=== OpenFIGI verdicts ===")
    for k in ("triple_match", "isin_identity_ok", "ticker_conflict", "ibkr_figi_mismatch", "no_figi"):
        if c.get(k):
            print(f"  {k:20} {c[k]:4}")
    flagged = [v for v in out.values() if v["verdict"] in ("ticker_conflict", "ibkr_figi_mismatch")]
    if flagged:
        print("\n  needs attention:")
        for v in flagged:
            print(f"    {v['verdict']:18} {v['ticker']:8} bb='{v['bb_name']}' | ibkr='{v['ibkr_name']}' | figi='{v['figi_name']}'")


if __name__ == "__main__":
    sys.exit(main())
