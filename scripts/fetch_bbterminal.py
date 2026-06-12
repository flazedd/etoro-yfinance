"""Pull the scheduled strategy's holdings from the bbterminal admin API.

Reads BBTERMINAL_BASE_URL and BBTERMINAL_API_TOKEN from .env and, using plain
`requests`:
  1. GET /api/admin/health        — go/no-go gate
  2. GET /api/admin/schedules      — find the (single) scheduled strategy
  3. GET /api/admin/schedules/{id} — its current order-ready holdings

Prints the holdings so we can eyeball what we'd try to buy on the paper account.

    .venv/bin/python scripts/fetch_bbterminal.py

Exit codes:
  0  fetched holdings successfully
  1  API reachable but unhealthy / unauthorized / no schedule
  2  configuration error (missing env var)
"""

from __future__ import annotations

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ.get("BBTERMINAL_BASE_URL", "").rstrip("/")
TOKEN = os.environ.get("BBTERMINAL_API_TOKEN", "")
TIMEOUT = 30.0


def _get(path: str, **params: str) -> requests.Response:
    return requests.get(
        f"{BASE_URL}{path}",
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"},
        params=params or None,
        timeout=TIMEOUT,
    )


def main() -> int:
    if not BASE_URL or not TOKEN:
        print("missing BBTERMINAL_BASE_URL or BBTERMINAL_API_TOKEN in .env", file=sys.stderr)
        return 2

    print("-- /api/admin/health --")
    r = _get("/api/admin/health")
    if r.status_code in (401, 403):
        print(f"unauthorized (HTTP {r.status_code}): token rejected", file=sys.stderr)
        return 1
    r.raise_for_status()
    health = r.json()
    print(health)
    if not health.get("is_healthy", False):
        print(f"NOT healthy; failed checks: {health.get('failed_checks')}", file=sys.stderr)
        # Keep going so we can still inspect schedules, but flag it.

    print("\n-- /api/admin/schedules?enabled_only=true --")
    r = _get("/api/admin/schedules", enabled_only="true")
    r.raise_for_status()
    schedules = r.json()
    print(f"{len(schedules)} scheduled strategy(ies):")
    for s in schedules:
        print(
            f"  id={s['strategy_id']} {s['name']!r} enabled={s['enabled']} "
            f"freq={s['frequency']} next={s.get('next_rebalance_at')} "
            f"as_of={s.get('as_of_date')} holdings={s.get('holdings_count')}"
        )

    if not schedules:
        print("no scheduled strategies", file=sys.stderr)
        return 1
    if len(schedules) > 1:
        print(f"\nexpected 1 strategy, found {len(schedules)}; using the first", file=sys.stderr)

    strategy_id = schedules[0]["strategy_id"]

    print(f"\n-- /api/admin/schedules/{strategy_id} --")
    r = _get(f"/api/admin/schedules/{strategy_id}")
    r.raise_for_status()
    detail = r.json()
    holdings = detail.get("holdings", [])
    print(
        f"strategy {detail['strategy_id']} {detail['name']!r}: "
        f"{len(holdings)} holdings, as_of={detail.get('as_of_date')}, "
        f"latest_price={detail.get('latest_price_date')}"
    )
    for h in holdings:
        print(
            f"  {h.get('ticker'):8s} {h.get('exchange', ''):8s} {h.get('currency', ''):4s} "
            f"{h.get('side', ''):4s} w={h.get('target_weight')} "
            f"px_local={h.get('entry_price_local')} px_eur={h.get('entry_price_eur')} "
            f"({h.get('company_name')})"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
