"""Attach a liquidity figure to every resolved universe company.

Liquidity = average daily traded VALUE in EUR = IBKR's 90-day average daily
volume (snapshot field 7282, in shares) x the company's EUR close price (from
the cached universe). That's the "can I actually trade size in this name"
metric — used both to filter the tradeable set and to prioritise the mapping
review (check liquid + low-confidence names first).

    uv run python scripts/enrich_liquidity.py --sleep 0.5

Writes data/<slug>_liquidity.json: company_id -> {conid, avg_vol, close_eur,
adv_eur}. Resumable (skips company_ids already present unless --refresh).
Read-only; no orders.
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

DATA_DIR = Path("data")
_AVG_VOL_FIELD = "7282"  # IBKR: 90-day average daily volume (shares)
_LAST_FIELD = "31"
_BATCH = 40  # snapshot 500s above ~50 conids/request
_WARMUPS = 3  # the avg-vol field only fills after a few round-trips


def _to_float(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", default="leonteq")
    parser.add_argument("--source", choices=("snapshot", "resolution"), default="snapshot",
                        help="conids from the live mapping_snapshot.json (default, full universe) "
                             "or the legacy <slug>_ibkr_resolution.json artifact")
    parser.add_argument("--sleep", type=float, default=0.5, help="pause between snapshot batches")
    parser.add_argument("--refresh", action="store_true", help="re-fetch all (ignore cache)")
    args = parser.parse_args()

    # EUR close comes from the cached universe (same for both sources); the conid
    # set is what differs — the snapshot carries every resolved name, not just the
    # subset the stale resolution artifact happened to price.
    uni = {str(m["company_id"]): m
           for m in json.loads((DATA_DIR / f"{args.slug}_universe.json").read_text())["members"]}
    if args.source == "snapshot":
        rows = json.loads((DATA_DIR / "mapping_snapshot.json").read_text()).get("rows", [])
        resolved = [{"company_id": r["company_id"], "conid": r["conid"], "ticker": r.get("ticker")}
                    for r in rows if r.get("conid") and r.get("kind") != "etf"]
    else:
        res = json.loads((DATA_DIR / f"{args.slug}_ibkr_resolution.json").read_text())
        resolved = [x for x in res["results"].values()
                    if x.get("status") == "resolved" and x.get("conid")]

    out_path = DATA_DIR / f"{args.slug}_liquidity.json"
    out: dict[str, Any] = {} if args.refresh or not out_path.exists() else \
        json.loads(out_path.read_text()).get("results", {})

    todo = [x for x in resolved if str(x["company_id"]) not in out]
    print(f"{len(resolved)} resolved; {len(todo)} to price ({len(out)} cached)\n")
    if not todo:
        print("nothing to do")
        return 0

    by_conid = {int(x["conid"]): x for x in todo}

    from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError

    client = IBKRClient()
    with client:
        client.init_brokerage_session()
        # Prime the market-data feed: the first snapshot after init reliably
        # 500s ("cold" session), so warm it on a tiny request before the loop.
        conids = list(by_conid)
        for _ in range(3):
            try:
                client.marketdata_snapshot(conids[:2], fields=[_AVG_VOL_FIELD, _LAST_FIELD], warmups=2)
                break
            except IBKRError:
                time.sleep(2.0)
        for i in range(0, len(conids), _BATCH):
            chunk = conids[i : i + _BATCH]
            rows: list[dict[str, Any]] = []
            for attempt in range(3):
                try:
                    rows = client.marketdata_snapshot(
                        chunk, fields=[_AVG_VOL_FIELD, _LAST_FIELD], warmups=_WARMUPS
                    )
                    break
                except IBKRError as e:
                    if attempt < 2:
                        time.sleep(2.0 * (attempt + 1))
                        continue
                    print(f"  batch {i // _BATCH} failed: {e}", file=sys.stderr)
            got = {int(r["conid"]): r for r in rows if r.get("conid") is not None}
            for cid in chunk:
                bb = by_conid[cid]
                m = uni.get(str(bb["company_id"]), {})
                close_eur = _to_float(m.get("latest_close_eur"))
                avg_vol = _to_float((got.get(cid) or {}).get(f"{_AVG_VOL_FIELD}_raw"))
                adv_eur = (avg_vol * close_eur) if (avg_vol and close_eur) else None
                out[str(bb["company_id"])] = {
                    "company_id": bb["company_id"], "ticker": bb["ticker"],
                    "conid": cid, "avg_vol": avg_vol, "close_eur": close_eur,
                    "adv_eur": round(adv_eur) if adv_eur else None,
                }
            done = min(i + _BATCH, len(conids))
            priced = sum(1 for cid in conids[:done] if out.get(str(by_conid[cid]["company_id"]), {}).get("adv_eur"))
            print(f"  [{done:4}/{len(conids)}] priced_so_far~{priced}")
            out_path.write_text(json.dumps({"slug": args.slug, "results": out}, indent=2))
            if args.sleep:
                time.sleep(args.sleep)

    have = [v["adv_eur"] for v in out.values() if v.get("adv_eur")]
    print(f"\nwrote {out_path}: {len(have)}/{len(out)} have an ADV figure")
    if have:
        have.sort()
        for label, frac in [("p10", 0.1), ("median", 0.5), ("p90", 0.9)]:
            print(f"  {label:6} ADV ~ EUR {have[int(frac * (len(have) - 1))]:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
