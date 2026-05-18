"""End-to-end test of target-portfolio fetching + validation.

Calls fetch_target_portfolio() against the given URL and pretty-prints the
parsed TargetPortfolio so you can eyeball the round-trip.

    uv run python scripts/test_target_fetch.py http://localhost:8765/target-portfolio.example.json
"""

from __future__ import annotations

import sys

from ibkr_portfolio_connect.target import TargetFetchError, fetch_target_portfolio


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: test_target_fetch.py <url>", file=sys.stderr)
        return 2

    url = sys.argv[1]
    try:
        target = fetch_target_portfolio(url)
    except TargetFetchError as e:
        print(f"FETCH FAILED: {e}", file=sys.stderr)
        return 1

    print(f"schema_version : {target.schema_version}")
    print(f"generated_at   : {target.generated_at.isoformat()}")
    print(f"base_currency  : {target.base_currency}")
    print(f"cash_buffer_pct: {target.cash_buffer_pct}")
    print(f"positions      : {len(target.positions)}")
    total_weight = sum(p.weight_pct for p in target.positions)
    for p in target.positions:
        print(f"  {p.symbol:6s} {p.exchange:8s} {p.asset_class:4s} {p.weight_pct:>6}%")
    print(f"sum(weights) + cash_buffer = {total_weight + target.cash_buffer_pct}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
