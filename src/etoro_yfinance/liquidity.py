"""Per-instrument liquidity measures.

Turnover side (free, from the EUR store): median daily €-turnover over a trailing
window (`adv_eur`), plus the fraction of no-trade days (`zero_vol_frac`). Turnover
is the standard cross-sectional liquidity screen — "don't trade names below €X/day".

Spread side (from eToro live bid/ask): `spread_pct` = (ask−bid)/mid × 100 — the
direct round-trip cost on eToro.

`rank_adv()` turns raw €-turnover into a 0–100 universe percentile so you can keep
"top N% most liquid". Pure math, shared by the build scripts and the web overlay.
"""
from __future__ import annotations

from typing import Any

WINDOW = 252  # trailing trading days for the turnover stats (~1 year)


def turnover_stats(volume_eur) -> dict[str, Any]:
    """From a EUR turnover series (data/prices_eur volume) → adv_eur (median daily
    €-turnover over the last WINDOW days), zero_vol_frac, and obs (days used)."""
    s = volume_eur.dropna()
    if len(s) == 0:
        return {"adv_eur": None, "zero_vol_frac": None, "obs": 0}
    s = s.tail(WINDOW)
    return {
        "adv_eur": float(s.median()),
        "zero_vol_frac": float((s <= 0).mean()),
        "obs": len(s),
    }


def spread_pct(rate: dict[str, Any] | None) -> float | None:
    """(ask−bid)/mid × 100 from a market-rates record, or None if unavailable."""
    if not rate:
        return None
    bid, ask = rate.get("bid"), rate.get("ask")
    if not bid or not ask or bid <= 0 or ask <= 0:
        return None
    mid = (bid + ask) / 2
    return (ask - bid) / mid * 100 if mid else None


def rank_adv(adv_by_key: dict[str, float]) -> dict[str, float]:
    """Map {key: adv_eur} → {key: percentile 0–100} (100 = most liquid)."""
    vals = sorted(v for v in adv_by_key.values() if v is not None)
    n = len(vals)
    if n == 0:
        return {}
    import bisect

    return {k: round(100 * bisect.bisect_right(vals, v) / n, 1)
            for k, v in adv_by_key.items() if v is not None}
