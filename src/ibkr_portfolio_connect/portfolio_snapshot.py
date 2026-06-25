"""Portfolio snapshot — IBKR positions + account summary -> local JSON.

Run by the credentialed side (the trader user) on a timer. It is the IBKR
analogue of `publisher.py`: it holds broker creds, talks to IBKR, and writes a
plain JSON file that the read-only web process renders on the /portfolio page.
The web NEVER calls IBKR itself — it only reads data/portfolio_snapshot.json.

    momentum-portfolio-snapshot            # fetch + write data/portfolio_snapshot.json

Config (env, shared with the rebalancer):
  IBKR_ACCOUNT_ID     the account to snapshot
  SIZING_CURRENCY     expected NAV currency (default EUR), for the headline only
  MOMENTUM_DATA_DIR   where to write the snapshot (default: data)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .config import Settings
from .ibkr_client import IBKRClient
from .schema import CurrentPosition
from .web.data import gurufocus_url

log = logging.getLogger(__name__)

# Account-summary fields worth surfacing on the page (IBKR lowercases its keys).
_SUMMARY_FIELDS = (
    "netliquidation",
    "totalcashvalue",
    "grosspositionvalue",
    "availablefunds",
    "buyingpower",
    "unrealizedpnl",
    "realizedpnl",
)


def _money(value: Any) -> dict[str, Any] | None:
    """Normalize an IBKR summary cell into {amount, currency}.

    Cells arrive as `{"amount": X, "currency": "EUR"}` or a bare number; return
    None for anything that won't parse so the page can render an em dash.
    """
    if value is None:
        return None
    if isinstance(value, dict):
        amount = value.get("amount", value.get("value"))
        currency = value.get("currency")
    else:
        amount, currency = value, None
    try:
        amt = float(Decimal(str(amount)))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return {"amount": amt, "currency": currency}


def _position_row(p: CurrentPosition, nav: float | None) -> dict[str, Any]:
    mv = float(p.market_value)
    return {
        "conid": p.conid,
        "symbol": p.symbol,
        "asset_class": p.asset_class,
        "quantity": float(p.quantity),
        "market_value": mv,
        "currency": p.currency,
        "mkt_price": float(p.mkt_price) if p.mkt_price is not None else None,
        "weight_pct": (mv / nav * 100.0) if nav else None,
        "gurufocus_url": gurufocus_url(None, None, p.symbol),
    }


def build_snapshot(client: IBKRClient, account_id: str, *, base_currency: str) -> dict[str, Any]:
    """Pull positions + account summary for one account into a plain dict."""
    summary = client.portfolio_summary(account_id)
    positions = client.positions(account_id)

    nav_cell = _money(summary.get("netliquidation"))
    nav = nav_cell["amount"] if nav_cell else None

    rows = [_position_row(p, nav) for p in positions]
    rows.sort(key=lambda r: abs(r["market_value"]), reverse=True)
    total_mv = sum(r["market_value"] for r in rows)

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "account_id": account_id,
        "base_currency": base_currency,
        "nav": nav_cell,
        "total_market_value": total_mv,
        "n_positions": len(rows),
        "summary": {f: _money(summary.get(f)) for f in _SUMMARY_FIELDS if f in summary},
        "positions": rows,
    }


def write_local(snapshot: dict[str, Any], data_dir: Path | None = None) -> Path:
    data_dir = data_dir or Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "portfolio_snapshot.json"
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()
    parser = argparse.ArgumentParser(description="Snapshot the IBKR portfolio for the web UI")
    parser.add_argument("--account", default=None, help="account id (default: IBKR_ACCOUNT_ID)")
    args = parser.parse_args()

    settings = Settings()  # type: ignore[call-arg]  # pydantic-settings reads env
    account_id = args.account or settings.ibkr_account_id

    with IBKRClient(timeout=settings.http_timeout_seconds) as client:
        snapshot = build_snapshot(client, account_id, base_currency=settings.sizing_currency)

    out = write_local(snapshot)
    nav = snapshot["nav"]
    print(f"wrote {out} — {snapshot['n_positions']} positions, "
          f"NAV {nav['amount'] if nav else '?'} {nav['currency'] if nav else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
