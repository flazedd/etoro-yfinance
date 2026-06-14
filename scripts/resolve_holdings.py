"""Resolve every bbterminal holding to a concrete IBKR conid.

Pulls the scheduled strategy's holdings from bbterminal, then resolves each
(ticker, exchange, currency) to a single IBKR STK contract via the
exchange-aware resolver. Prints a table and exits nonzero if any holding can't
be resolved — the gate that proves we know *exactly* what we'd buy.

    uv run python scripts/resolve_holdings.py

Exit codes:
  0  every holding resolved to one IBKR conid
  1  one or more holdings unresolved (see the table)
  2  configuration error / OAuth not active
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect.bbterminal_client import (  # noqa: E402
    BBTerminalClient,
    BBTerminalError,
)
from ibkr_portfolio_connect.contract_resolver import (  # noqa: E402
    ContractResolutionError,
    resolve_contract,
)


def main() -> int:
    try:
        bb = BBTerminalClient.from_env()
        scheds = bb.schedules(enabled_only=True)
    except BBTerminalError as e:
        print(f"bbterminal error: {e}", file=sys.stderr)
        return 2
    if not scheds:
        print("no enabled scheduled strategies", file=sys.stderr)
        return 1
    strategy_id = scheds[0]["strategy_id"]
    detail = bb.schedule(strategy_id)
    holdings = detail.get("holdings", [])
    print(
        f"strategy #{strategy_id} {detail.get('name')!r}: {len(holdings)} holdings "
        f"as_of={detail.get('as_of_date')}\n"
    )

    try:
        from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError
    except Exception as e:  # pragma: no cover
        print(f"could not import IBKR client: {e}", file=sys.stderr)
        return 2
    try:
        client = IBKRClient()
    except Exception as e:
        print(f"FAILED to construct IBKRClient (OAuth): {e}", file=sys.stderr)
        return 2

    unresolved: list[str] = []
    print(f"  {'TICKER':10} {'EXCH':6} {'CCY':4} {'CONID':>10}  {'IBKR':9} {'SYMBOL':8} VIA")
    with client:
        for h in holdings:
            ticker = str(h.get("ticker", "")).strip()
            exch = str(h.get("exchange", "")).strip()
            ccy = str(h.get("currency", "")).strip()
            isin = str(h.get("isin", "")).strip() or None
            if not ticker:
                continue
            try:
                rc = resolve_contract(client, ticker, exch, ccy, isin=isin)
            except (ContractResolutionError, IBKRError) as e:
                print(f"  {ticker:10} {exch:6} {ccy:4} {'—':>10}  UNRESOLVED: {e}")
                unresolved.append(ticker)
                continue
            print(
                f"  {ticker:10} {exch:6} {ccy:4} {rc.conid:>10}  {rc.ibkr_listing:9} "
                f"{rc.ibkr_symbol:8} {rc.method}"
            )

    print()
    total = len([h for h in holdings if str(h.get("ticker", "")).strip()])
    print(f"resolved {total - len(unresolved)}/{total}")
    if unresolved:
        print(f"UNRESOLVED: {', '.join(unresolved)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
