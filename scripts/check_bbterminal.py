"""End-to-end pre-flight check for the rebalancer's two upstreams.

Milestone 1 — before we trade anything, prove three things:

  1. We can authenticate to bbterminal (Supabase email/password -> JWT) and
     our account has the `admin` role.
  2. We can read the current target portfolio (the scheduled strategy's
     order-ready holdings) and the pipeline is healthy.
  3. Every holding's ticker actually resolves to a tradeable contract on
     IBKR (secdef/search), so we know up front which names we could buy.

This PLACES NO ORDERS and needs no account write access — it's a read-only
sanity gate. Run it on your dev machine (or the Pi) any time.

    uv run python scripts/check_bbterminal.py
    uv run python scripts/check_bbterminal.py --skip-ibkr   # bbterminal only

Exit codes:
  0  authenticated, holdings read, and every ticker resolved on IBKR
  1  reachable but something failed a gate (not admin / unhealthy / a ticker
     did not resolve / OAuth not yet active)
  2  configuration error (missing env var, missing key file)
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

# IBind reads IBIND_* env vars at import time, so load .env before importing
# anything from our package (which transitively imports ibind).
load_dotenv()

from ibkr_portfolio_connect.bbterminal_client import (  # noqa: E402
    BBTerminalClient,
    BBTerminalError,
)


def _summarize(rows: list[dict]) -> tuple[bool, str]:  # type: ignore[type-arg]
    """Summarize raw IBKR secdef/search rows: (has_stk_match, human string).

    A ticker is considered 'available' if any row exposes a STK section.
    We also surface the listing exchanges so foreign names can be eyeballed.
    """
    has_stk = False
    parts: list[str] = []
    for r in rows:
        if r.get("symbol") is None:
            continue
        sectypes: set[str] = set()
        exchanges: set[str] = set()
        for sec in r.get("sections") or []:
            st = str(sec.get("secType", "")).upper()
            if st:
                sectypes.add(st)
            ex = str(sec.get("exchange", "") or "")
            if ex:
                exchanges.update(e.strip() for e in ex.split(",") if e.strip())
        if "STK" in sectypes:
            has_stk = True
        desc = str(r.get("description") or r.get("companyHeader") or "").strip()
        exch_str = ",".join(sorted(exchanges)) if exchanges else "?"
        parts.append(
            f"conid={r.get('conid')} {r.get('symbol')}"
            + (f" [{desc[:40]}]" if desc else "")
            + f" types={','.join(sorted(sectypes)) or '?'} @ {exch_str}"
        )
    return has_stk, "\n           ".join(parts) if parts else "(no matches)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--skip-ibkr",
        action="store_true",
        help="only check bbterminal auth + holdings; skip IBKR availability",
    )
    args = parser.parse_args()

    # ---- 1. bbterminal auth -------------------------------------------------
    print("=== bbterminal: authenticate ===")
    try:
        bb = BBTerminalClient.from_env()
    except BBTerminalError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2

    try:
        me = bb.whoami()
    except BBTerminalError as e:
        print(f"login/whoami failed: {e}", file=sys.stderr)
        return 1
    role = me.get("role")
    print(f"  authenticated as {me.get('email')}  id={me.get('id')}  role={role}")
    if role != "admin":
        print(
            f"  WARNING: role is {role!r}, not 'admin' — /api/admin/* endpoints "
            "will 403. Ask for an admin role on this account.",
            file=sys.stderr,
        )

    # ---- 2. health + holdings ----------------------------------------------
    print("\n=== bbterminal: health ===")
    try:
        health = bb.health()
    except BBTerminalError as e:
        print(f"health failed: {e}", file=sys.stderr)
        return 1
    strict = health.get("is_healthy_strict")
    print(f"  is_healthy_strict={strict}")
    if health.get("problems"):
        print(f"  problems={health.get('problems')}")

    print("\n=== bbterminal: scheduled strategies ===")
    try:
        scheds = bb.schedules(enabled_only=True)
    except BBTerminalError as e:
        print(f"schedules failed: {e}", file=sys.stderr)
        return 1
    if not scheds:
        print("  no enabled scheduled strategies — nothing to read", file=sys.stderr)
        return 1
    for s in scheds:
        print(
            f"  #{s.get('strategy_id')} {s.get('name')!r} "
            f"next={s.get('next_rebalance_at')} as_of={s.get('as_of_date')} "
            f"holdings={s.get('holdings_count')}"
        )
    if len(scheds) > 1:
        print(f"  (found {len(scheds)} strategies; using the first)")
    strategy_id = scheds[0]["strategy_id"]

    print(f"\n=== bbterminal: holdings for strategy #{strategy_id} ===")
    try:
        detail = bb.schedule(strategy_id)
    except BBTerminalError as e:
        print(f"schedule({strategy_id}) failed: {e}", file=sys.stderr)
        return 1
    holdings = detail.get("holdings", [])
    print(
        f"  {detail.get('name')!r}: {len(holdings)} holdings, "
        f"as_of={detail.get('as_of_date')} latest_price={detail.get('latest_price_date')}"
    )
    currencies = sorted({str(h.get("currency", "?")) for h in holdings})
    print(f"  currencies present: {', '.join(currencies)}")
    for h in holdings:
        print(
            f"    {str(h.get('side', '')).upper():5} {h.get('ticker', '')!s:10} "
            f"{h.get('exchange', '')!s:8} {h.get('country', '')!s:4} "
            f"{h.get('currency', '')!s:4} w={h.get('target_weight')} "
            f"({h.get('company_name')})"
        )

    if args.skip_ibkr:
        print("\n--skip-ibkr set; not checking IBKR availability.")
        return 0

    # ---- 3. IBKR availability ----------------------------------------------
    print("\n=== IBKR: resolve each ticker (secdef/search) ===")
    try:
        from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError
    except Exception as e:  # pragma: no cover
        print(f"could not import IBKR client: {e}", file=sys.stderr)
        return 2

    try:
        client = IBKRClient()
    except Exception as e:
        print(f"FAILED to construct IBKRClient (OAuth): {e}", file=sys.stderr)
        print(
            "If you see 'invalid consumer', OAuth has not been activated by IBKR yet. "
            "Re-run with --skip-ibkr to check bbterminal alone.",
            file=sys.stderr,
        )
        return 1

    unresolved: list[str] = []
    with client:
        for h in holdings:
            ticker = str(h.get("ticker", "")).strip()
            exch = str(h.get("exchange", "")).strip()
            name = str(h.get("company_name", "")).strip()
            if not ticker:
                continue
            try:
                rows = client.secdef_search_raw(ticker)
            except IBKRError as e:
                print(f"  ERR  {ticker:10} ({exch:5}) {name[:28]:28} {e}")
                unresolved.append(ticker)
                continue
            has_stk, summary = _summarize(rows)
            mark = "OK  " if has_stk else "MISS"
            if not has_stk:
                unresolved.append(ticker)
            print(f"  {mark} {ticker:10} ({exch:5}) {name[:28]:28} -> {summary}")

    print()
    total = len([h for h in holdings if str(h.get("ticker", "")).strip()])
    resolved = total - len(unresolved)
    print(f"resolved {resolved}/{total} tickers on IBKR")
    if unresolved:
        print(f"NOT resolved as STK: {', '.join(unresolved)}", file=sys.stderr)
        print(
            "These need attention before trading: wrong/foreign ticker symbol, "
            "a listing IBKR names differently, or an exchange the account can't access.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
