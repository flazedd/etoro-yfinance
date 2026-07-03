"""Read-only loaders for the web app — the eToro→yfinance universe snapshot.

The only input is a plain JSON file under the data directory (no credentials, no
network), built offline by scripts/etoro_universe.py.
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


_COVERAGE_KEYS = ("price_from", "price_to", "vol_from", "vol_to", "bars")


def _overlay_coverage(doc: dict[str, Any]) -> dict[str, Any]:
    """Overlay the live validation cache (yf_validation_cache.json) onto the rows,
    so the web reflects Yahoo coverage as it is built — one row at a time, every
    ~100 tickers — instead of waiting for the end-of-run mapping rewrite. The
    cache maps a yfinance ticker to {price_from, price_to, vol_from, vol_to, bars}.
    """
    rows = doc.get("rows")
    if not rows:
        return doc
    cache = _load(data_dir() / "yf_validation_cache.json")
    for r in rows:
        c = cache.get(r.get("yf")) if r.get("yf") else None
        if c:
            for k in _COVERAGE_KEYS:
                r[k] = c.get(k)
            r["yf_price_ok"] = bool(c.get("price_from"))
            r["yf_vol_ok"] = bool(c.get("vol_from"))
            r["yf_ok"] = r["yf_price_ok"] and r["yf_vol_ok"]
    # Show the coverage columns if we have any coverage data — live from the cache
    # mid-run, or already baked into the rows by a completed run.
    has_coverage = bool(cache) or any("price_from" in r for r in rows)
    doc.setdefault("counts", {})["validated"] = has_coverage
    return doc


def _overlay_eligibility(doc: dict[str, Any]) -> dict[str, Any]:
    """Overlay eToro trading-rule summary fields (tradable / min $ / max leverage
    / shortable) from the live eligibility cache, keyed by instrument_id. The full
    rule set is fetched on demand by the /universe/rules endpoint, so rows stay
    light. Mirrors _overlay_coverage's live-vs-baked behaviour."""
    rows = doc.get("rows")
    if not rows:
        return doc
    from etoro_yfinance.eligibility import SUMMARY_KEYS, summarize

    cache = _load(data_dir() / "eligibility_cache.json")
    if cache:
        for r in rows:
            iid = r.get("instrument_id")
            if iid is not None and str(iid) in cache:
                e = cache[str(iid)]
                r.update(summarize(e) if e else dict.fromkeys(SUMMARY_KEYS))
            else:
                # Keep the summary keys defined (None) so templates can test them,
                # without clobbering values already baked into the mapping row.
                for k in SUMMARY_KEYS:
                    r.setdefault(k, None)
    has_rules = bool(cache) or any("tradable" in r for r in rows)
    doc.setdefault("counts", {})["eligibility_checked"] = has_rules
    return doc


def _overlay_liquidity(doc: dict[str, Any]) -> dict[str, Any]:
    """Overlay liquidity onto rows: turnover stats (adv_eur, zero_vol_frac — by
    yfinance ticker) from the turnover cache, live spread_pct (by instrument_id)
    from the spread cache, and a universe percentile rank (adv_pct)."""
    rows = doc.get("rows")
    if not rows:
        return doc
    from etoro_yfinance import liquidity as liq

    turn = _load(data_dir() / "liquidity_cache.json")   # keyed by yfinance ticker
    spr = _load(data_dir() / "spread_cache.json")        # keyed by instrument_id
    for r in rows:
        yf = r.get("yf")
        t = turn.get(yf) if (turn and yf) else None
        if t:
            r["adv_eur"] = t.get("adv_eur")
            r["zero_vol_frac"] = t.get("zero_vol_frac")
        iid = r.get("instrument_id")
        s = spr.get(str(iid)) if (spr and iid is not None) else None
        if s:
            r["spread_pct"] = s.get("spread_pct")
        for k in ("adv_eur", "adv_pct", "zero_vol_frac", "spread_pct"):
            r.setdefault(k, None)

    adv_by_yf = {r["yf"]: r["adv_eur"] for r in rows
                 if r.get("yf") and r.get("adv_eur") is not None}
    ranks = liq.rank_adv(adv_by_yf)
    for r in rows:
        if r.get("yf") in ranks:
            r["adv_pct"] = ranks[r["yf"]]

    if turn or spr or any(r.get("adv_eur") is not None for r in rows):
        doc.setdefault("counts", {})["liquidity_checked"] = True
    return doc


def _overlay_sector(doc: dict[str, Any]) -> dict[str, Any]:
    """Fill ETF sectors live from the Yahoo fund-category cache (stocks/crypto
    sectors are baked into the row at build time)."""
    rows = doc.get("rows")
    if not rows:
        return doc
    cat = _load(data_dir() / "etf_category_cache.json")
    override = _load(data_dir() / "sector_override_cache.json")
    for r in rows:
        if cat and r.get("type") == "ETF" and r.get("yf") and cat.get(r["yf"]):
            r["sector"] = cat[r["yf"]]
        if override and not r.get("sector") and r.get("yf") and override.get(r["yf"]):
            r["sector"] = override[r["yf"]]   # Yahoo fallback for unclassified names
        r.setdefault("sector", None)
    if any(r.get("sector") for r in rows):
        doc.setdefault("counts", {})["sector_known"] = True
    return doc


def load_etoro_universe() -> dict[str, Any]:
    """The eToro universe → yfinance mapping written by
    `scripts/etoro_universe.py`: every eToro tradable instrument mapped to its
    yfinance analysis ticker (or flagged unmapped/internal). Empty dict if the
    builder hasn't run. Shape: `{generated_at, counts, exchanges, rows:[{instrument_id,
    symbol, name, type, exchange, yf, status, isin, price_from, price_to,
    vol_from, vol_to, bars}]}`. Coverage fields are overlaid live from the
    validation cache when present.
    """
    doc = _load(data_dir() / "etoro_universe_mapping.json")
    return _overlay_sector(_overlay_liquidity(_overlay_eligibility(_overlay_coverage(doc))))


def load_instrument_rules(instrument_id: str) -> dict[str, Any] | None:
    """Full eToro trading-rule record for one instrument id — live from the
    eligibility cache, else baked into the mapping row. None if unknown."""
    key = str(instrument_id)
    cache = _load(data_dir() / "eligibility_cache.json")
    if key in cache:
        return cache[key] or None
    for r in _load(data_dir() / "etoro_universe_mapping.json").get("rows", []):
        if str(r.get("instrument_id")) == key:
            return r.get("rules")
    return None


def snapshot_age_seconds(name: str, now: float) -> float | None:
    """Seconds since the named snapshot file in the data dir was last written,
    or None if it doesn't exist. `now` is passed in (caller owns the clock)."""
    path = data_dir() / name
    try:
        return max(0.0, now - path.stat().st_mtime)
    except OSError:
        return None
