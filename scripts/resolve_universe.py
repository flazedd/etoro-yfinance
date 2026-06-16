"""Cache a bbterminal universe locally, then check each company against IBKR.

Two phases, both idempotent so a long sweep can be re-run / resumed safely:

  1. Universe cache — fetch the universe membership ONCE from bbterminal and
     store it at data/<slug>_universe.json. Later runs read the file and never
     hit the API again (pass --refresh-universe to force a re-fetch).

  2. IBKR findability — for every company, look it up on IBKR (ISIN-first, the
     collision-free path) and classify it:

       resolved                on IBKR AND on our mapped exchange -> trading-ready
       found_unmapped_exchange on IBKR, but our bbterminal exchange isn't in the
                               resolver's map yet -> add a BBTERMINAL_TO_IBKR_LISTING entry
       found_wrong_exchange    mapped, but IBKR has no listing on the expected venue
       not_on_ibkr             IBKR doesn't know this ISIN/ticker
       error                   IBKR call failed (kept so a re-run retries it)

     Results stream to data/<slug>_ibkr_resolution.json keyed by company_id.
     Already-resolved companies are skipped on re-run (use --refresh-resolution
     to redo them, or --retry-errors to redo just the error/not_on_ibkr rows).

    uv run python scripts/resolve_universe.py                 # LEONTEQ, full sweep
    uv run python scripts/resolve_universe.py --limit 30      # smoke-test first
    uv run python scripts/resolve_universe.py --id 7          # a different universe
    uv run python scripts/resolve_universe.py --summary-only  # re-print the tally

This PLACES NO ORDERS (reference data only — works under any OAuth session).

Exit codes:
  0  swept the whole universe (some companies may still be unresolved — see tally)
  1  reachable but a gate failed (not admin / no matching universe)
  2  configuration error / OAuth not active
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect.bbterminal_client import (  # noqa: E402
    BBTerminalClient,
    BBTerminalError,
)
from ibkr_portfolio_connect.contract_resolver import (  # noqa: E402
    BBTERMINAL_TO_IBKR_LISTING,
    CONID_OVERRIDES,
    ContractResolutionError,
    _parse_isin_row,
    resolve_by_ticker,
)

DATA_DIR = Path("data")
# How often (in companies processed) to flush the resolution file to disk, so a
# kill mid-sweep loses at most this many lookups.
_FLUSH_EVERY = 25


def _slug(label: str) -> str:
    """'LEONTEQ (as of 2026-06-05)' -> 'leonteq'."""
    head = label.split("(", 1)[0].strip().lower()
    return "".join(c if c.isalnum() else "_" for c in head).strip("_") or "universe"


# ─── Phase 1: universe cache ─────────────────────────────────────────────────


def load_or_fetch_universe(
    bb: BBTerminalClient, universe_id: int, label: str, *, refresh: bool, month: str | None
) -> dict[str, Any]:
    path = DATA_DIR / f"{_slug(label)}_universe.json"
    if path.exists() and not refresh:
        print(f"  using cached universe -> {path}")
        return json.loads(path.read_text())
    print(f"  fetching universe #{universe_id} from bbterminal (slow, ~30s) ...")
    detail = bb.universe(universe_id, month=month)
    DATA_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(detail, indent=2))
    print(f"  cached {len(detail.get('members', []))} members -> {path}")
    return detail


# ─── Phase 2: IBKR findability ───────────────────────────────────────────────


def probe_member(client: Any, member: dict[str, Any]) -> dict[str, Any]:
    """Classify one universe member against IBKR. One ISIN search when an ISIN
    is present (tells us every venue IBKR lists it on, regardless of whether we
    map that exchange); ticker fallback otherwise."""
    from ibkr_portfolio_connect.ibkr_client import IBKRError

    isin = str(member.get("isin", "") or "").strip()
    exch = str(member.get("exchange", "") or "").strip()
    ticker = str(member.get("ticker", "") or "").strip()
    ccy = str(member.get("currency", "") or "").strip()
    expected = BBTERMINAL_TO_IBKR_LISTING.get(exch.upper())

    base = {
        "company_id": member.get("company_id"),
        "ticker": ticker,
        "exchange": exch,
        "currency": ccy,
        "isin": isin or None,
        "company_name": member.get("company_name"),
    }

    # A reviewed conid pin wins outright (no IBKR call needed).
    override = CONID_OVERRIDES.get((ticker.upper(), exch.upper()))
    if override:
        conid, ibkr_symbol, ibkr_listing = override
        return {**base, "status": "resolved", "method": "override",
                "conid": conid, "ibkr_listing": ibkr_listing, "ibkr_symbol": ibkr_symbol}

    if isin:
        try:
            rows = client.secdef_search_raw(isin)
        except IBKRError as e:
            return {**base, "status": "error", "note": str(e)[:200]}
        contracts = []
        for row in rows:
            parsed = _parse_isin_row(row) if isinstance(row, dict) else None
            if parsed:
                conid, symbol, venue = parsed
                contracts.append({"conid": conid, "symbol": symbol, "venue": venue})
        if contracts:
            venues = sorted({c["venue"] for c in contracts})
            base["ibkr_venues"] = venues
            if expected is None:
                return {**base, "status": "found_unmapped_exchange",
                        "note": f"on IBKR at {venues}; no map for bbterminal {exch!r}"}
            match = next((c for c in contracts if c["venue"] in expected), None)
            if match:
                return {**base, "status": "resolved", "method": "isin",
                        "conid": match["conid"], "ibkr_listing": match["venue"],
                        "ibkr_symbol": match["symbol"]}
            # ISIN matched only non-expected venues (often an ADR / wrong ISIN
            # line, e.g. Air Liquide's US OTC). Try the collision-safe ticker
            # path on the expected exchange before giving up.
            if ticker:
                try:
                    rc = resolve_by_ticker(client, ticker, exch, ccy)
                    return {**base, "status": "resolved", "method": "ticker",
                            "conid": rc.conid, "ibkr_listing": rc.ibkr_listing,
                            "ibkr_symbol": rc.ibkr_symbol, "ibkr_venues": venues}
                except (ContractResolutionError, IBKRError):
                    pass
            return {**base, "status": "found_wrong_exchange",
                    "note": f"on IBKR at {venues}; expected one of {sorted(expected)}"}
        # ISIN unknown to IBKR — fall through to ticker.

    # No ISIN, or ISIN unknown to IBKR. The collision-safe ticker path only works
    # for mapped exchanges; without a mapping we can't assert the right company.
    if expected is not None and ticker:
        try:
            rc = resolve_by_ticker(client, ticker, exch, ccy)
        except (ContractResolutionError, IBKRError) as e:
            return {**base, "status": "not_on_ibkr", "note": str(e)[:200]}
        return {**base, "status": "resolved", "method": "ticker",
                "conid": rc.conid, "ibkr_listing": rc.ibkr_listing,
                "ibkr_symbol": rc.ibkr_symbol}
    return {**base, "status": "not_on_ibkr",
            "note": "no ISIN on IBKR and exchange unmapped (can't ticker-search safely)"}


def _print_summary(results: dict[str, dict[str, Any]], total_members: int) -> None:
    by_status: Counter[str] = Counter(r.get("status", "?") for r in results.values())
    print(f"\n=== tally ({len(results)}/{total_members} companies probed) ===")
    for status in ("resolved", "found_unmapped_exchange", "found_wrong_exchange",
                   "not_on_ibkr", "error"):
        n = by_status.get(status, 0)
        if n:
            print(f"  {status:24} {n:5}")
    leftover = set(by_status) - {
        "resolved", "found_unmapped_exchange", "found_wrong_exchange",
        "not_on_ibkr", "error",
    }
    for status in sorted(leftover):
        print(f"  {status:24} {by_status[status]:5}")

    # Which bbterminal exchanges are findable-but-unmapped — the actionable list.
    unmapped: Counter[str] = Counter(
        r.get("exchange", "?") for r in results.values()
        if r.get("status") == "found_unmapped_exchange"
    )
    if unmapped:
        print("\n  exchanges to add to BBTERMINAL_TO_IBKR_LISTING (count = companies):")
        for exch, n in unmapped.most_common():
            sample = next(
                (r.get("ibkr_venues") for r in results.values()
                 if r.get("exchange") == exch and r.get("ibkr_venues")),
                None,
            )
            print(f"    {exch:8} {n:5}   IBKR venues seen e.g. {sample}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--match", default="leonteq", help="find universe by label substring")
    parser.add_argument("--id", type=int, default=None, help="universe_id (skips --match)")
    parser.add_argument("--month", default=None, help="YYYY-MM (LongEquity time-series only)")
    parser.add_argument("--refresh-universe", action="store_true", help="re-fetch the cached universe")
    parser.add_argument("--refresh-resolution", action="store_true", help="re-probe every company")
    parser.add_argument("--retry-errors", action="store_true", help="re-probe only error/not_on_ibkr rows")
    parser.add_argument("--retry-unresolved", action="store_true", help="re-probe everything not yet 'resolved' (use after editing the exchange map)")
    parser.add_argument("--reapply-overrides", action="store_true", help="re-probe every company with a CONID_OVERRIDES pin (use after editing overrides; no IBKR calls)")
    parser.add_argument("--limit", type=int, default=0, help="only probe the first N companies (0 = all)")
    parser.add_argument("--timeout", type=int, default=90, help="bbterminal request timeout (s)")
    parser.add_argument("--sleep", type=float, default=0.0, help="seconds to pause between IBKR lookups (throttle to avoid 429 IP blocks)")
    parser.add_argument("--summary-only", action="store_true", help="print the saved tally and exit")
    args = parser.parse_args()

    # ---- auth + discover the universe --------------------------------------
    try:
        bb = BBTerminalClient.from_env()
    except BBTerminalError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2
    bb.timeout = args.timeout
    try:
        me = bb.whoami()
        universes = bb.universes()
    except BBTerminalError as e:
        print(f"bbterminal error: {e}", file=sys.stderr)
        return 1
    if me.get("role") != "admin":
        print(f"not admin (role={me.get('role')!r}) — /api/admin/* will 403", file=sys.stderr)
        return 1

    if args.id is not None:
        target = next((u for u in universes if u.get("universe_id") == args.id), None)
        if target is None:
            target = {"universe_id": args.id, "label": f"id_{args.id}"}
    else:
        needle = args.match.lower()
        target = next(
            (u for u in universes
             if needle in f"{u.get('label','')} {u.get('description','')}".lower()),
            None,
        )
        if target is None:
            print(f"no universe matching {args.match!r}; available:", file=sys.stderr)
            for u in universes:
                print(f"  #{u.get('universe_id')} {u.get('label')!r}", file=sys.stderr)
            return 1

    uid = int(target["universe_id"])
    label = str(target.get("label", f"id_{uid}"))
    print(f"=== universe #{uid} {label!r} ===")

    # ---- phase 1: cache membership -----------------------------------------
    detail = load_or_fetch_universe(
        bb, uid, label, refresh=args.refresh_universe, month=args.month
    )
    members = detail.get("members", [])
    if args.limit:
        members = members[: args.limit]
    if not members:
        print("universe has no members", file=sys.stderr)
        return 1

    res_path = DATA_DIR / f"{_slug(label)}_ibkr_resolution.json"
    saved: dict[str, Any] = (
        json.loads(res_path.read_text()) if res_path.exists() else {}
    )
    results: dict[str, dict[str, Any]] = dict(saved.get("results", {}))

    if args.summary_only:
        _print_summary(results, detail.get("member_count") or len(detail.get("members", [])))
        return 0

    # Decide which company_ids still need work.
    retry_statuses = {"error", "not_on_ibkr"}
    todo = []
    for m in members:
        cid = str(m.get("company_id"))
        prior = results.get(cid)
        has_override = (
            str(m.get("ticker", "")).upper(),
            str(m.get("exchange", "")).upper(),
        ) in CONID_OVERRIDES
        if (
            prior is None
            or args.refresh_resolution
            or (args.retry_errors and prior.get("status") in retry_statuses)
            or (args.retry_unresolved and prior.get("status") != "resolved")
            or (args.reapply_overrides and has_override)
        ):
            todo.append(m)
    print(
        f"\n=== IBKR findability: {len(todo)} to probe "
        f"({len(results)} already done, {len(members)} in scope) ===\n"
    )

    if todo:
        from ibkr_portfolio_connect.ibkr_client import IBKRClient
        try:
            client = IBKRClient()
        except Exception as e:
            print(f"FAILED to construct IBKRClient (OAuth): {e}", file=sys.stderr)
            return 2

        def _flush() -> None:
            res_path.parent.mkdir(exist_ok=True)
            res_path.write_text(json.dumps(
                {"universe_id": uid, "label": label,
                 "updated_at": datetime.now(UTC).isoformat(),
                 "results": results}, indent=2))

        try:
            with client:
                for i, m in enumerate(todo, 1):
                    r = probe_member(client, m)
                    results[str(m.get("company_id"))] = r
                    mark = {"resolved": "OK  ", "found_unmapped_exchange": "MAP ",
                            "found_wrong_exchange": "WEXC", "not_on_ibkr": "MISS",
                            "error": "ERR "}.get(r["status"], "??  ")
                    print(
                        f"  [{i:4}/{len(todo)}] {mark} {r['ticker']:10} {r['exchange']:6} "
                        f"{r['currency']:4} -> {r['status']}"
                        + (f" conid={r['conid']} {r.get('ibkr_listing','')}" if r.get("conid") else "")
                    )
                    if i % _FLUSH_EVERY == 0:
                        _flush()
                    if args.sleep:
                        time.sleep(args.sleep)
        finally:
            _flush()
            print(f"\n  wrote {res_path}")

    _print_summary(results, detail.get("member_count") or len(detail.get("members", [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
