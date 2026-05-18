"""Place a single market DAY order against an IBKR account.

For one-off ad-hoc trades and smoke-testing order placement against the paper
account once OAuth is active. NOT for the monthly cron — use the
`ibkr-portfolio-connect` CLI for that.

Examples:
    # Resolve + plan only, do not place:
    uv run python scripts/place_trade.py VOO BUY 1 --account DUQ970095 --dry-run

    # Place for real (with confirmation prompt):
    uv run python scripts/place_trade.py VOO BUY 1 --account DUQ970095

    # Place without prompt (paper accounts only — be careful):
    uv run python scripts/place_trade.py VOO BUY 1 --account DUQ970095 --yes

The exchange flag is used for conid resolution only; orders always route SMART.
Defaults to ARCA, which covers most common ETFs (VOO, VTI, BND, VXUS, ...).
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from dotenv import load_dotenv

# IBind reads IBIND_* env vars at import time, so load .env before importing
# anything from our package (which transitively imports ibind).
load_dotenv()

from ibkr_portfolio_connect.ibkr_client import IBKRClient, IBKRError  # noqa: E402
from ibkr_portfolio_connect.schema import OrderSide  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

TERMINAL = {"Filled", "Cancelled", "Rejected", "Inactive"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Place a single MKT DAY order against IBKR.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("symbol", help="ticker symbol (e.g. VOO)")
    parser.add_argument("side", choices=["BUY", "SELL"])
    parser.add_argument("quantity", type=int, help="whole shares (>0)")
    parser.add_argument(
        "--account",
        required=True,
        help="IBKR account ID (e.g. DUQxxxxxxx for paper, Uxxxxxxx for live)",
    )
    parser.add_argument(
        "--exchange",
        default="ARCA",
        help="listing exchange for conid resolution (default: ARCA)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="resolve conid + print plan, don't place"
    )
    parser.add_argument("--yes", action="store_true", help="skip confirmation prompt")
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=60.0,
        help="how long to poll for terminal status (default: 60s)",
    )
    args = parser.parse_args()

    if args.quantity <= 0:
        print("quantity must be positive", file=sys.stderr)
        return 2

    side = OrderSide.BUY if args.side == "BUY" else OrderSide.SELL

    print("Connecting to IBKR via OAuth ...")
    try:
        client = IBKRClient()
    except Exception as e:
        print(f"\nFAILED to construct IBKRClient: {e}", file=sys.stderr)
        print("If you see 'invalid consumer', OAuth has not been activated yet.", file=sys.stderr)
        return 2

    with client:
        # Sanity-check the account is visible to OAuth.
        try:
            accounts = client.iserver_accounts()
        except IBKRError as e:
            print(f"FAILED to list accounts: {e}", file=sys.stderr)
            return 1
        print(f"  visible accounts: {accounts}")
        if accounts and args.account not in accounts:
            print(
                f"WARNING: {args.account!r} is not in the visible list; "
                "IBKR may still accept it but double-check the ID.",
                file=sys.stderr,
            )

        print(f"\nResolving {args.symbol} on {args.exchange} ...")
        try:
            conid = client.resolve_conid(args.symbol, args.exchange)
        except IBKRError as e:
            print(f"FAILED: {e}", file=sys.stderr)
            return 1
        print(f"  conid={conid}")

        print("\n=== Planned order ===")
        print(f"  Account:  {args.account}")
        print(f"  Action:   {side.value} {args.quantity} share(s)")
        print(f"  Symbol:   {args.symbol} (conid {conid})")
        print("  Type:     MKT DAY (routed SMART)")

        if args.dry_run:
            print("\n--dry-run set; not placing.")
            return 0

        if not args.yes:
            confirm = input("\nProceed? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Aborted.")
                return 0

        print("\nPlacing order ...")
        try:
            replies = client.place_midprice_day_order(
                args.account, conid=conid, side=side, quantity=args.quantity
            )
        except IBKRError as e:
            print(f"PLACE FAILED: {e}", file=sys.stderr)
            return 1

        if not replies:
            print("UNEXPECTED: empty reply from place_order", file=sys.stderr)
            return 1

        first = replies[0]
        if first.kind == "error":
            print(f"REJECTED: {first.error}", file=sys.stderr)
            return 1
        if first.kind != "confirmed" or not first.order_id:
            print(
                f"UNEXPECTED reply shape: {first.model_dump(exclude_none=True)}",
                file=sys.stderr,
            )
            return 1

        order_id = first.order_id
        print(f"  submitted: order_id={order_id}  status={first.order_status}")

        print(f"\nPolling for terminal status (up to {args.poll_seconds:.0f}s) ...")
        deadline = time.monotonic() + args.poll_seconds
        last_status: str | None = None
        status = first.order_status or "?"
        while True:
            blob = client.order_status(order_id)
            status = str(
                blob.get("order_status")
                or blob.get("status")
                or blob.get("order_ccp_status")
                or "?"
            )
            if status != last_status:
                print(f"  status: {status}")
                last_status = status
            if status in TERMINAL:
                break
            if time.monotonic() >= deadline:
                print(
                    f"\nTimed out after {args.poll_seconds:.0f}s "
                    f"with status={status!r}; the order may still fill."
                )
                return 0
            time.sleep(2)

        print(f"\nFinal status: {status}")
        return 0 if status == "Filled" else 1


if __name__ == "__main__":
    sys.exit(main())
