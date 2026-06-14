"""Build / refresh / verify the pinned conid map.

Three modes:

    # Resolve current holdings, update the map, flag new/changed for review:
    uv run python scripts/sync_conid_map.py

    # Same, then mark everything resolved this run as reviewed (after you've
    # eyeballed the table):
    uv run python scripts/sync_conid_map.py --approve-all

    # Pre-trade gate — no IBKR, no writes. Verify every current holding has a
    # reviewed, non-drifted entry. This is what the bot runs before trading:
    uv run python scripts/sync_conid_map.py --check

Exit codes:
  0  all good (synced cleanly / check passed)
  1  something needs a human: unresolved holding, or an entry pending review /
     drifted (in --check)
  2  configuration error / OAuth not active
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect.bbterminal_client import (  # noqa: E402
    BBTerminalClient,
    BBTerminalError,
)
from ibkr_portfolio_connect.conid_map import (  # noqa: E402
    DEFAULT_MAP_PATH,
    ConidMapError,
    classify,
    load_map,
    make_entry,
    require_reviewed_conid,
    save_map,
)
from ibkr_portfolio_connect.contract_resolver import (  # noqa: E402
    ContractResolutionError,
    resolve_contract,
)


def _holdings() -> tuple[int, list[dict]]:
    bb = BBTerminalClient.from_env()
    scheds = bb.schedules(enabled_only=True)
    if not scheds:
        raise BBTerminalError("no enabled scheduled strategies")
    strategy_id = scheds[0]["strategy_id"]
    detail = bb.schedule(strategy_id)
    return strategy_id, detail.get("holdings", [])


def _check(path: Path) -> int:
    """Pure pre-trade gate: every current holding must be reviewed in the map."""
    try:
        strategy_id, holdings = _holdings()
    except BBTerminalError as e:
        print(f"bbterminal error: {e}", file=sys.stderr)
        return 2
    m = load_map(path)
    problems: list[str] = []
    for h in holdings:
        try:
            conid = require_reviewed_conid(
                m, int(h["company_id"]), expected_isin=(str(h["isin"]) if h.get("isin") else None)
            )
        except ConidMapError as e:
            problems.append(str(e))
            continue
        print(f"  OK  {h.get('ticker','')!s:10} company_id={h['company_id']} -> conid {conid}")
    print()
    if problems:
        print(f"CHECK FAILED ({len(problems)} problem(s)):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"CHECK OK — all {len(holdings)} holdings of strategy #{strategy_id} are reviewed")
    return 0


def _sync(path: Path, approve_all: bool) -> int:
    try:
        strategy_id, holdings = _holdings()
    except BBTerminalError as e:
        print(f"bbterminal error: {e}", file=sys.stderr)
        return 2

    from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError

    try:
        client = IBKRClient()
    except Exception as e:
        print(f"FAILED to construct IBKRClient (OAuth): {e}", file=sys.stderr)
        return 2

    m = load_map(path)
    m.strategy_id = strategy_id
    now = datetime.now(UTC).isoformat()
    added: list[str] = []
    changed: list[str] = []
    unchanged: list[str] = []
    unresolved: list[str] = []

    with client:
        for h in holdings:
            ticker = str(h.get("ticker", "")).strip()
            cid = int(h["company_id"])
            try:
                rc = resolve_contract(
                    client,
                    ticker,
                    str(h.get("exchange", "")),
                    str(h.get("currency", "")),
                    isin=(str(h["isin"]) if h.get("isin") else None),
                )
            except (ContractResolutionError, IBKRError) as e:
                print(f"  UNRESOLVED {ticker:10} company_id={cid}: {e}", file=sys.stderr)
                unresolved.append(ticker)
                continue

            existing = m.get(cid)
            status = classify(existing, rc.conid)
            # unchanged keeps its prior reviewed flag; added/changed need review
            # unless --approve-all. The flag can only be raised, never lowered,
            # by approve-all on an unchanged reviewed entry.
            if status == "unchanged" and existing is not None:
                reviewed = existing.reviewed or approve_all
            else:
                reviewed = approve_all

            m.put(
                make_entry(
                    h,
                    conid=rc.conid,
                    ibkr_symbol=rc.ibkr_symbol,
                    ibkr_listing=rc.ibkr_listing,
                    resolved_via=rc.method,
                    reviewed=reviewed,
                    now=now,
                )
            )
            tag = "" if reviewed else "  [NEEDS REVIEW]"
            line = f"  {status.upper():9} {ticker:10} conid={rc.conid} {rc.ibkr_listing}/{rc.ibkr_symbol} via {rc.method}{tag}"
            print(line)
            {"added": added, "changed": changed, "unchanged": unchanged}[status].append(ticker)

    m.generated_at = now
    save_map(m, path)
    print(
        f"\nwrote {path}: +{len(added)} added, ~{len(changed)} changed, "
        f"={len(unchanged)} unchanged, !{len(unresolved)} unresolved"
    )

    pending = [e.ticker for e in m.entries.values() if not e.reviewed]
    if unresolved:
        print(f"UNRESOLVED (need attention): {', '.join(unresolved)}", file=sys.stderr)
    if pending:
        print(
            f"PENDING REVIEW: {', '.join(sorted(pending))}\n"
            "  Eyeball the contracts above, then re-run with --approve-all "
            "(or edit conid_map.json and set reviewed: true).",
            file=sys.stderr,
        )
    return 1 if (unresolved or pending) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", type=Path, default=DEFAULT_MAP_PATH, help="map file (default: conid_map.json)")
    parser.add_argument("--approve-all", action="store_true", help="mark all entries resolved this run as reviewed")
    parser.add_argument("--check", action="store_true", help="pre-trade gate: verify reviewed coverage, no IBKR/writes")
    args = parser.parse_args()

    if args.check:
        return _check(args.path)
    return _sync(args.path, args.approve_all)


if __name__ == "__main__":
    sys.exit(main())
