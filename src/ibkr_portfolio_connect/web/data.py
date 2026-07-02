"""Read-only loaders for the web app — universe mapping + performance snapshot.

All inputs are plain JSON files under the data directory (no credentials, no
network). The universe rows merge the four pipeline artifacts the same way
build_review_site.py does, so the page mirrors the offline review tool.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def data_dir() -> Path:
    return Path(os.environ.get("MOMENTUM_DATA_DIR", "data"))


def _load(path: Path) -> dict[str, Any]:
    try:
        data: dict[str, Any] = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return data


def gurufocus_url(country: str | None, exch: str | None, ticker: str | None) -> str:
    """US exchanges -> ticker only; everywhere else EXCH:TICKER."""
    if not ticker:
        return ""
    sym = ticker if country == "United States" else f"{exch}:{ticker}"
    return f"https://www.gurufocus.com/stock/{sym}/summary"


def load_mapping() -> dict[str, Any]:
    """The unified instrument-mapping snapshot written by the credentialed
    `momentum-mapping-snapshot` job: every LEONTEQ universe member + every ETF,
    each resolved to its tradeable IBKR conid (or an `error` row with a reason).

    The web never calls bbterminal or IBKR — it only reads
    data/mapping_snapshot.json. Empty dict if the job hasn't run yet, in which
    case the page renders a hint. Shape: `{generated_at, universe_id, label,
    counts:{...}, rows:[{kind, name, isin, ticker, conid, status, ...}]}`.
    """
    return _load(data_dir() / "mapping_snapshot.json")


def load_performance() -> dict[str, Any]:
    """The performance snapshot written by the credentialed publisher.

    Empty dict if the publisher hasn't run yet — the page renders a hint.
    """
    return _load(data_dir() / "performance_snapshot.json")


def load_portfolio() -> dict[str, Any]:
    """The live IBKR portfolio snapshot written by the credentialed snapshotter
    (`momentum-portfolio-snapshot`). The web never calls IBKR; it only reads this
    file. Empty dict if the snapshotter hasn't run yet — the page renders a hint.
    """
    return _load(data_dir() / "portfolio_snapshot.json")


def load_strategies() -> dict[str, Any]:
    """The scheduled-strategies snapshot written by the credentialed
    `momentum-strategies-snapshot` job: every enabled scheduled strategy and its
    current bbterminal holdings. The web never calls bbterminal; it only reads
    data/strategies_snapshot.json. Empty dict if the job hasn't run yet — the
    page renders a hint. Shape: `{generated_at, count, strategies:[{strategy_id,
    name, next_rebalance_at, holdings:[...]}]}`.
    """
    return _load(data_dir() / "strategies_snapshot.json")


def snapshot_age_seconds(name: str, now: float) -> float | None:
    """Seconds since the named snapshot file in the data dir was last written,
    or None if it doesn't exist. `now` is passed in (caller owns the clock)."""
    path = data_dir() / name
    try:
        return max(0.0, now - path.stat().st_mtime)
    except OSError:
        return None
