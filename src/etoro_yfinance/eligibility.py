"""Flatten an eToro instrument-eligibility record into a few at-a-glance fields.

The full record (position limits, permitted order types, SL/TP bounds, per
settlement-type/direction leverage) is stored verbatim per row as `rules`; this
derives the compact columns (tradable / min $ / max leverage / shortable) shown
inline in the universe table. Pure dict math, no deps — shared by the probe
(scripts/etoro_universe.py) and the web overlay (web/data.py).
"""

from __future__ import annotations

from typing import Any


def summarize(e: dict[str, Any]) -> dict[str, Any]:
    configs = e.get("leverageConfigs") or []
    levs = [v for c in configs for v in (c.get("leverageValues") or [])]
    return {
        "tradable": bool(e.get("allowOpenPosition")),
        "closable": bool(e.get("allowClosePosition")),
        "min_exposure": e.get("minPositionExposure"),
        "max_leverage": max(levs) if levs else None,
        "shortable": any(c.get("direction") == "short" for c in configs),
    }


# Keys written onto each row from summarize() — used to clear/merge consistently.
SUMMARY_KEYS = ("tradable", "closable", "min_exposure", "max_leverage", "shortable")
