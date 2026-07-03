"""Select a backtestable, executable eToro universe from the enriched snapshot.

Criteria (all derived from the mapping + caches, via web.data.load_etoro_universe):
  - mapped to a yfinance ticker (us/intl/crypto)
  - has BOTH price and volume history
  - tradable on eToro right now (allowOpenPosition) — execution is guaranteed
  - enough history (min_bars) and recent (not stale — price_to within recent_days)
  - minimum €/day turnover (liquidity floor)
  - has a derived sector (optional; sector_gap() lists the ones that miss only this)

Spread is carried (spread_pct) as a per-instrument cost input for the backtest,
and optionally hard-filtered via max_spread. Backtest on the EUR series
(prices.load_matrix(tickers, eur=True)) for cross-market comparability.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, date, datetime, timedelta

MAPPED = ("us", "intl", "crypto")

# Persisted per instrument in a saved universe (execution id + analysis ticker + metrics).
FIELDS = ("instrument_id", "symbol", "name", "yf", "type", "exchange", "sector",
          "adv_eur", "spread_pct", "bars", "price_from", "price_to",
          "min_exposure", "max_leverage")


def _cutoff(rows, recent_days: int | None) -> str:
    """The oldest acceptable price_to (latest closed session minus recent_days)."""
    latest = max((r.get("price_to") or "" for r in rows), default="")
    if not latest or not recent_days:
        return ""
    y, m, d = (int(x) for x in latest.split("-"))
    return str(date(y, m, d) - timedelta(days=recent_days))


def _load_rows():
    from etoro_yfinance.web.data import load_etoro_universe
    return load_etoro_universe().get("rows", [])


def select(*, min_adv: float = 1_000_000.0, min_bars: int = 252,
           recent_days: int | None = 7, max_spread: float | None = None,
           require_sector: bool = True, rows: list | None = None) -> list[dict]:
    """The instruments passing every criterion. `rows` defaults to the live
    enriched snapshot; pass your own to reuse one load."""
    rows = rows if rows is not None else _load_rows()
    cutoff = _cutoff(rows, recent_days)
    out = []
    for r in rows:
        if r.get("status") not in MAPPED or not r.get("yf"):
            continue
        if not (r.get("price_from") and r.get("vol_from")):     # price + volume
            continue
        if not r.get("tradable"):                                # executable on eToro
            continue
        if (r.get("adv_eur") or 0) < min_adv:                    # liquidity floor
            continue
        if (r.get("bars") or 0) < min_bars:                      # enough history
            continue
        if cutoff and (r.get("price_to") or "") < cutoff:        # not stale
            continue
        if max_spread is not None and (r.get("spread_pct") is None
                                       or r.get("spread_pct") > max_spread):
            continue
        if require_sector and not r.get("sector"):
            continue
        out.append(r)
    return out


def sector_gap(*, rows: list | None = None, **criteria) -> list[dict]:
    """Instruments passing every criterion EXCEPT having a sector — the
    candidates to backfill a sector for (scripts/backfill_sectors.py)."""
    rows = rows if rows is not None else _load_rows()
    criteria.pop("require_sector", None)
    passing = select(rows=rows, require_sector=False, **criteria)
    return [r for r in passing if not r.get("sector")]


# ── saved universes ──────────────────────────────────────────────────────────
def _safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", (name or "").strip()) or "backtest"


def _path(name: str):
    from etoro_yfinance.web.data import data_dir
    return data_dir() / f"universe_{_safe_name(name)}.json"


def list_saved() -> list[str]:
    from etoro_yfinance.web.data import data_dir
    d = data_dir()
    return sorted(p.stem[len("universe_"):] for p in d.glob("universe_*.json"))


def load(name: str) -> dict:
    p = _path(name)
    return json.loads(p.read_text()) if p.exists() else {}


def member_ids(name: str) -> set:
    return {r.get("instrument_id") for r in load(name).get("instruments", [])}


def verify(selected: list[dict], *, min_adv: float, min_bars: int, **_) -> dict:
    """Per-condition pass counts over a selected set (each should equal total)."""
    return {
        "price + volume": sum(1 for r in selected if r.get("price_from") and r.get("vol_from")),
        "tradable on eToro": sum(1 for r in selected if r.get("tradable")),
        f"turnover ≥ €{min_adv:,.0f}/day": sum(
            1 for r in selected if (r.get("adv_eur") or 0) >= min_adv),
        f"history ≥ {min_bars} bars": sum(
            1 for r in selected if (r.get("bars") or 0) >= min_bars),
        "has sector": sum(1 for r in selected if r.get("sector")),
        "total": len(selected),
    }


def save(name: str, *, rows: list | None = None, require_sector: bool = True,
         **criteria) -> dict:
    """Select under the criteria, persist to data/universe_<name>.json, and return
    the doc (with per-sector counts and per-condition verification)."""
    rows = rows if rows is not None else _load_rows()
    sel = select(rows=rows, require_sector=require_sector, **criteria)
    doc = {
        "generated_at": datetime.now(UTC).isoformat(),
        "name": _safe_name(name),
        "criteria": {**criteria, "require_sector": require_sector},
        "count": len(sel),
        "by_sector": dict(Counter(r.get("sector") or "—" for r in sel).most_common()),
        "checks": verify(sel, **criteria),
        "instruments": [{k: r.get(k) for k in FIELDS} for r in sel],
    }
    _path(name).write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    return doc
