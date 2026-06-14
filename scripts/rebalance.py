"""Run a buy/replace rebalance from the bbterminal strategy.

DRY-RUN BY DEFAULT — prints the planned trades and places nothing. Pass
--execute to actually send orders (only do this once the plan looks right and,
for first runs, against the paper account).

    uv run python scripts/rebalance.py              # plan only, no orders
    uv run python scripts/rebalance.py --execute    # place orders

Preconditions (all gated, will abort with a clear message):
  * bbterminal health.is_healthy_strict is true (or REQUIRE_STRATEGY_HEALTHY=false)
  * every holding is a reviewed entry in conid_map.json (run sync_conid_map.py)
  * account NAV is in the sizing currency (EUR)

Exit codes:
  0  completed (plan printed, or orders placed with no failures)
  1  a precondition / safety gate aborted, or a trade failed
  2  configuration error
"""

from __future__ import annotations

import argparse
import logging
import sys

from dotenv import load_dotenv

load_dotenv()

from ibkr_portfolio_connect.bb_rebalance import (  # noqa: E402
    RebalanceInputError,
    run_bb_rebalance,
)
from ibkr_portfolio_connect.bbterminal_client import BBTerminalError  # noqa: E402
from ibkr_portfolio_connect.config import Settings  # noqa: E402
from ibkr_portfolio_connect.conid_map import ConidMapError  # noqa: E402
from ibkr_portfolio_connect.cost import RebalanceReport  # noqa: E402
from ibkr_portfolio_connect.safety import PreTradeSafetyError  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _print_report(report: RebalanceReport, *, executed: bool) -> None:
    print("\n=== Rebalance report ===")
    print(f"  NAV (EUR): {report.nav}")
    print(f"  mode: {'EXECUTED' if executed else 'DRY RUN'}")
    if report.aborted_reason:
        print(f"  ABORTED: {report.aborted_reason}")
        return
    if not report.trades:
        print("  no trades — already in line with target")
        return
    for c in report.trades:
        line = f"  {c.trade.side.value:4} {c.trade.quantity:>6} {c.trade.symbol:10} ({c.trade.reason})"
        if executed:
            line += f"  -> {c.final_status or '?'}"
            if c.fill_price is not None:
                line += f" @ {c.fill_price}"
            if not c.success and c.error:
                line += f"  ERROR: {c.error}"
        print(line)
    print(
        f"  {report.n_successful}/{report.n_total} ok"
        + (f", {report.n_failed} failed" if report.n_failed else "")
    )
    if executed:
        print(
            f"  cost: {report.total_cost_dollars} EUR "
            f"({report.total_cost_pct_of_nav:.3f}% of NAV); "
            f"slip {report.total_slippage_dollars}, comm {report.total_commission_dollars}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execute", action="store_true", help="place orders (default is dry-run)")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt when executing")
    args = parser.parse_args()

    try:
        settings = Settings()  # type: ignore[call-arg]
    except Exception as e:
        print(f"config error: {e}", file=sys.stderr)
        return 2

    if args.execute and not args.yes:
        print(f"About to place REAL orders on account {settings.ibkr_account_id}.")
        if input("Proceed? [y/N]: ").strip().lower() not in ("y", "yes"):
            print("Aborted.")
            return 0

    try:
        report = run_bb_rebalance(settings, dry_run=not args.execute)
    except (RebalanceInputError, ConidMapError, PreTradeSafetyError) as e:
        print(f"\nGATE FAILED: {e}", file=sys.stderr)
        return 1
    except BBTerminalError as e:
        print(f"\nbbterminal error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"\nFAILED: {e}", file=sys.stderr)
        return 1

    _print_report(report, executed=args.execute)
    return 0 if report.overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
