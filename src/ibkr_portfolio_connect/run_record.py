"""Per-run audit snapshot — the structured record the dashboard renders.

`cost.save_report` already persists the slippage/fill attribution, but the
dashboard wants the WHOLE story of a run: when it started, which gates passed,
the NAV it sized against, current-vs-target positions, the planned trades, the
fills, and how it ended. `RunRecorder` collects that incrementally and writes
one JSON file per run to `report_dir/{started:%Y%m%d-%H%M%S}.json`.

It is written at every checkpoint (not just at the end) so that a run which
crashes or hangs still leaves a record with `status="running"` — a visible
"this run never finished" signal in the dashboard, rather than nothing at all.

Everything here is best-effort and defensive: a serialization hiccup must never
abort a rebalance, so `persist()` swallows its own errors (logged, not raised).
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# status values, in lifecycle order
RUNNING = "running"
ABORTED = "aborted"  # a pre-trade gate/safety check refused to trade
DRY_RUN = "dry_run"
SUCCESS = "success"
PARTIAL = "partial"  # some trades placed, some failed
FAILED = "failed"  # all trades failed
ERROR = "error"  # an unexpected exception


def _json_default(o: Any) -> Any:
    if isinstance(o, Decimal):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, Path):
        return str(o)
    return str(o)


class RunRecorder:
    """Mutable, incrementally-persisted record of one rebalance run."""

    def __init__(
        self,
        report_dir: Path | None,
        *,
        dry_run: bool,
        now: datetime | None = None,
    ) -> None:
        self._report_dir = report_dir
        self._started = now or datetime.now(UTC)
        self.data: dict[str, Any] = {
            "started_at": self._started.isoformat(),
            "finished_at": None,
            "status": RUNNING,
            "dry_run": dry_run,
            "strategy_id": None,
            "as_of_date": None,
            "health": None,
            "sizing_currency": None,
            "nav": None,
            "targets": [],
            "current_positions": [],
            "planned_trades": [],
            "report": None,
            "abort_reason": None,
            "error": None,
        }

    @property
    def path(self) -> Path | None:
        if self._report_dir is None:
            return None
        return self._report_dir / f"{self._started.strftime('%Y%m%d-%H%M%S')}.json"

    def update(self, **fields: Any) -> None:
        """Merge fields into the record and re-persist."""
        self.data.update(fields)
        self.persist()

    def finish(self, status: str, *, now: datetime | None = None, **fields: Any) -> None:
        self.data.update(fields)
        self.data["status"] = status
        self.data["finished_at"] = (now or datetime.now(UTC)).isoformat()
        self.persist()

    def persist(self) -> None:
        """Write the current record. Best-effort: never raises into the caller."""
        path = self.path
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.data, indent=2, default=_json_default))
        except OSError as e:  # disk full, perms, etc. — log, don't abort trading
            log.warning("could not persist run record to %s: %s", path, e)


# ---- defensive serializers for the messy upstream shapes -------------------


def summarize_targets(targets: list[Any]) -> list[dict[str, Any]]:
    """ResolvedTarget -> a small JSON-safe dict for the dashboard."""
    out: list[dict[str, Any]] = []
    for t in targets:
        out.append(
            {
                "conid": getattr(t, "conid", None),
                "symbol": getattr(t, "symbol", None),
                "exchange": getattr(t, "exchange", None),
                "weight_pct": _opt_str(getattr(t, "weight_pct", None)),
                "reference_price": _opt_str(getattr(t, "reference_price", None)),
            }
        )
    return out


def summarize_positions(positions: list[Any]) -> list[dict[str, Any]]:
    """IBKR positions come back as dicts with varying key spellings; pull the
    few fields the dashboard shows, tolerating whatever isn't present."""
    out: list[dict[str, Any]] = []
    for p in positions:
        d = p if isinstance(p, dict) else getattr(p, "__dict__", {})
        out.append(
            {
                "conid": d.get("conid") or d.get("conidEx"),
                "symbol": d.get("contractDesc") or d.get("ticker") or d.get("symbol"),
                "position": _num(d.get("position")),
                "mkt_value": _num(d.get("mktValue") or d.get("marketValue")),
                "currency": d.get("currency"),
            }
        )
    return out


def summarize_trades(trades: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for t in trades:
        side = getattr(t, "side", None)
        out.append(
            {
                "side": getattr(side, "value", side),
                "quantity": getattr(t, "quantity", None),
                "symbol": getattr(t, "symbol", None),
                "conid": getattr(t, "conid", None),
                "reason": getattr(t, "reason", None),
                "reference_price": _opt_str(getattr(t, "reference_price", None)),
            }
        )
    return out


def status_from_report(report: Any) -> str:
    """Map a RebalanceReport's outcome onto a record status."""
    if getattr(report, "dry_run", False):
        return DRY_RUN
    if getattr(report, "overall_success", False):
        return SUCCESS
    if report.n_successful > 0:
        return PARTIAL
    return FAILED


def _opt_str(d: Any) -> str | None:
    return str(d) if d is not None else None


def _num(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
