"""Buy / sell / preview against an eToro account — standalone, no IBKR.

Uses `EtoroClient` (broker-agnostic) and eToro's public REST API. Credentials
come from .env: ETORO_API_KEY, ETORO_USER_KEY, ETORO_ENV (demo|real). A key is
environment-scoped, so ETORO_ENV must match the key you created in the eToro API
Portal. Defaults to DEMO — flip ETORO_ENV=real (with a real-env key) for live.

Examples:
    # Resolve a ticker to an eToro instrument id:
    uv run python scripts/etoro_trade.py resolve AAPL

    # Account value (NAV / cash):
    uv run python scripts/etoro_trade.py balance

    # Preview the cost of a $100 buy (no order placed):
    uv run python scripts/etoro_trade.py preview AAPL --amount 100

    # Buy $100 of AAPL (confirmation prompt unless --yes):
    uv run python scripts/etoro_trade.py buy AAPL --amount 100

    # Sell = close 2 units of an existing position (needs its eToro ids):
    uv run python scripts/etoro_trade.py sell --position-id 2150941015 --instrument-id 1001 --units 2
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()

from etoro_yfinance.broker import BrokerError  # noqa: E402
from etoro_yfinance.config import Settings  # noqa: E402
from etoro_yfinance.etoro_client import etoro_from_settings  # noqa: E402


def _confirm(env: str, action: str) -> bool:
    tag = "DEMO (virtual money)" if env == "demo" else "*** REAL MONEY ***"
    ans = input(f"\n{tag} — proceed to {action}? [y/N]: ").strip().lower()
    return ans in ("y", "yes")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Buy/sell/preview against eToro.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("balance", help="show account value (NAV / cash)")

    p_res = sub.add_parser("resolve", help="ticker -> eToro instrument id")
    p_res.add_argument("symbol")

    for name, help_ in (
        ("preview", "cost breakdown for a buy (no order)"),
        ("buy", "open a long at market"),
    ):
        p = sub.add_parser(name, help=help_)
        p.add_argument("symbol")
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--amount", type=Decimal, help="notional amount (in order currency)")
        g.add_argument("--units", type=Decimal, help="number of units")
        if name == "buy":
            p.add_argument("--yes", action="store_true", help="skip confirmation prompt")

    p_sell = sub.add_parser("sell", help="close (sell) units of an existing position")
    p_sell.add_argument("--position-id", required=True, help="eToro positionId to close")
    p_sell.add_argument("--instrument-id", required=True, help="the position's instrumentId")
    p_sell.add_argument(
        "--units", type=Decimal, default=None, help="units to close (default: entire position)"
    )
    p_sell.add_argument("--yes", action="store_true", help="skip confirmation prompt")

    args = parser.parse_args()
    settings = Settings()  # type: ignore[call-arg]

    try:
        client = etoro_from_settings(settings)
    except BrokerError as e:
        print(f"FAILED to construct EtoroClient: {e}", file=sys.stderr)
        return 2

    with client:
        print(f"eToro environment: {settings.etoro_env}")
        try:
            if args.cmd == "balance":
                b = client.balance()
                print(f"  NAV (total): {b.total} {b.currency}")
                print(f"  cash:        {b.cash} {b.currency}")
                return 0

            if args.cmd == "resolve":
                inst = client.resolve_symbol(args.symbol)
                print(
                    f"  {inst.symbol} -> instrumentId={inst.instrument_id} "
                    f"({inst.name} {inst.currency})"
                )
                return 0

            if args.cmd in ("preview", "buy"):
                inst = client.resolve_symbol(args.symbol)
                print(f"  resolved {inst.symbol} -> instrumentId={inst.instrument_id}")
                prev = client.preview_buy(instrument=inst, amount=args.amount, units=args.units)
                print("\n=== Cost preview ===")
                for line in prev.lines:
                    print(f"  {line.kind:<16} {line.amount} {line.currency}")
                print(f"  {'TOTAL':<16} {prev.est_cost} {prev.currency}")
                if args.cmd == "preview":
                    return 0
                if not args.yes and not _confirm(settings.etoro_env, f"BUY {inst.symbol}"):
                    print("Aborted.")
                    return 0
                res = client.buy(instrument=inst, amount=args.amount, units=args.units)
                print(f"\nOrder submitted: orderId={res.order_id} status={res.status}")
                return 0

            if args.cmd == "sell":
                if not args.yes and not _confirm(
                    settings.etoro_env, f"CLOSE position {args.position_id}"
                ):
                    print("Aborted.")
                    return 0
                res = client.close_position(
                    position_id=args.position_id,
                    instrument_id=args.instrument_id,
                    units=args.units,
                )
                print(f"Close submitted: orderId={res.order_id} status={res.status}")
                return 0
        except BrokerError as e:
            print(f"FAILED: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
