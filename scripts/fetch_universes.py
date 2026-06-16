"""List bbterminal universes and dump one universe's membership.

Step 1 of the universe-trading track: prove we can discover the available
universes and pull the full membership of the Leonteq one (ticker / exchange /
country / currency / isin per company) — the inputs we'd later resolve to IBKR
contracts.

    uv run python scripts/fetch_universes.py
    uv run python scripts/fetch_universes.py --match leonteq   # default
    uv run python scripts/fetch_universes.py --include-all     # also live/derived
    uv run python scripts/fetch_universes.py --id 42           # pull by id directly

This PLACES NO ORDERS and needs no IBKR access — read-only against bbterminal.

Exit codes:
  0  listed universes and dumped the matched universe's membership
  1  reachable but a gate failed (not admin / no matching universe)
  2  configuration error (missing env var)
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect.bbterminal_client import (  # noqa: E402
    BBTerminalClient,
    BBTerminalError,
)


def _pick(universes: list[dict], match: str) -> dict | None:  # type: ignore[type-arg]
    """First universe whose label/description contains `match` (case-insensitive)."""
    needle = match.lower()
    for u in universes:
        hay = f"{u.get('label', '')} {u.get('description', '')}".lower()
        if needle in hay:
            return u
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--match",
        default="leonteq",
        help="substring to find the universe by label/description (default: leonteq)",
    )
    parser.add_argument(
        "--id",
        type=int,
        default=None,
        help="pull this universe_id directly, skipping the --match search",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="also list live template / time-series / derived / index universes",
    )
    parser.add_argument(
        "--month",
        default=None,
        help="YYYY-MM snapshot (only affects the multi-month LongEquity universe)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="per-request timeout in seconds (the membership call is heavy: "
        "LEONTEQ is ~1600 members / ~0.5MB and takes ~30s; default 90)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="max member rows to print (0 = all); LEONTEQ is ~1600 (default 25)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="optional path to write the full membership JSON",
    )
    args = parser.parse_args()

    # ---- auth ---------------------------------------------------------------
    print("=== bbterminal: authenticate ===")
    try:
        bb = BBTerminalClient.from_env()
    except BBTerminalError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2
    bb.timeout = args.timeout
    try:
        me = bb.whoami()
    except BBTerminalError as e:
        print(f"login/whoami failed: {e}", file=sys.stderr)
        return 1
    print(f"  authenticated as {me.get('email')}  role={me.get('role')}")
    if me.get("role") != "admin":
        print("  WARNING: not 'admin' — /api/admin/* will 403", file=sys.stderr)

    # ---- list universes -----------------------------------------------------
    print(f"\n=== bbterminal: universes (include_all={args.include_all}) ===")
    try:
        universes = bb.universes(include_all=args.include_all)
    except BBTerminalError as e:
        print(f"universes() failed: {e}", file=sys.stderr)
        return 1
    if not universes:
        print("  no universes returned", file=sys.stderr)
        return 1
    for u in universes:
        print(
            f"  #{u.get('universe_id')} {u.get('label')!r} kind={u.get('kind')} "
            f"as_of={u.get('as_of_date')} members={u.get('member_count')}"
        )

    # ---- pick the target universe ------------------------------------------
    if args.id is not None:
        target = next((u for u in universes if u.get("universe_id") == args.id), None)
        if target is None:
            # Not in the (possibly filtered) list — try fetching it directly anyway.
            target = {"universe_id": args.id, "label": f"id={args.id}"}
    else:
        target = _pick(universes, args.match)
        if target is None:
            print(
                f"\nno universe matching {args.match!r}. "
                "Try --include-all, or pick an --id from the list above.",
                file=sys.stderr,
            )
            return 1

    uid = target["universe_id"]
    print(f"\n=== bbterminal: membership for #{uid} {target.get('label')!r} ===")
    try:
        detail = bb.universe(uid, month=args.month)
    except BBTerminalError as e:
        print(f"universe({uid}) failed: {e}", file=sys.stderr)
        return 1
    members = detail.get("members", [])
    print(
        f"  {detail.get('label')!r}: {len(members)} members, "
        f"frozen_at={detail.get('frozen_at')} target_month={detail.get('target_month')}"
    )
    currencies = sorted({str(m.get("currency", "?")) for m in members})
    print(f"  currencies present: {', '.join(currencies)}")
    shown = members if args.limit == 0 else members[: args.limit]
    for m in shown:
        print(
            f"    {m.get('ticker', '')!s:10} {m.get('exchange', '')!s:8} "
            f"{m.get('country', '')!s:4} {m.get('currency', '')!s:4} "
            f"isin={m.get('isin', '')!s:14} "
            f"close_eur={m.get('latest_close_eur')} "
            f"({m.get('company_name')})"
        )
    if len(shown) < len(members):
        print(f"    … {len(members) - len(shown)} more (use --limit 0 to print all)")

    if args.out:
        import json
        from pathlib import Path

        with Path(args.out).open("w") as fh:
            json.dump(detail, fh, indent=2)
        print(f"\n  wrote full membership JSON -> {args.out}")

    if not members:
        print("\nuniverse has no members.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
