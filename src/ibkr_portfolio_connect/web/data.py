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


def load_universe_rows(slug: str = "leonteq") -> list[dict[str, Any]]:
    """Join universe + verification + liquidity + openfigi into per-company rows."""
    d = data_dir()
    uni = _load(d / f"{slug}_universe.json").get("members", [])
    ver = _load(d / f"{slug}_mapping_verification.json").get("results", {})
    liq = _load(d / f"{slug}_liquidity.json").get("results", {})
    fig = _load(d / f"{slug}_openfigi.json").get("results", {})

    by_cid = {str(m.get("company_id")): m for m in uni}
    rows: list[dict[str, Any]] = []
    # Drive off the universe so unmapped names still show (with blank IBKR cols).
    for cid, m in by_cid.items():
        v = ver.get(cid, {})
        lq = liq.get(cid, {})
        fg = fig.get(cid, {})
        country = m.get("country")
        ticker = m.get("ticker")
        exch = m.get("exchange")
        rows.append({
            "cid": cid,
            "bb_name": m.get("company_name"),
            "ibkr_name": v.get("ibkr_name"),
            "ticker": ticker,
            "ibkr_sym": v.get("ibkr_symbol"),
            "tmatch": v.get("ticker_match"),
            "lmatch": v.get("listing_match"),
            "exch": exch,
            "listing": v.get("ibkr_listing"),
            "country": country,
            "currency": m.get("currency"),
            "ccy_ok": v.get("ccy_ok", True),
            "isin": m.get("isin"),
            "conid": v.get("conid"),
            "score": v.get("name_score"),
            "conf": v.get("confidence") or ("unresolved" if not v else "?"),
            "figi": fg.get("verdict"),
            "adv": lq.get("adv_eur"),
            "gf": gurufocus_url(country, exch, ticker),
        })
    rows.sort(key=lambda r: (r["bb_name"] or "").lower())
    return rows


def universe_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    by_conf: dict[str, int] = {}
    for r in rows:
        by_conf[r["conf"]] = by_conf.get(r["conf"], 0) + 1
    resolved = sum(1 for r in rows if r.get("conid"))
    tmatch = sum(1 for r in rows if r.get("tmatch"))
    with_adv = sum(1 for r in rows if r.get("adv"))
    return {
        "total": total,
        "resolved": resolved,
        "ticker_match": tmatch,
        "with_adv": with_adv,
        "high": by_conf.get("high", 0),
        "medium": by_conf.get("medium", 0),
        "low": by_conf.get("low", 0),
    }


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


def snapshot_age_seconds(name: str, now: float) -> float | None:
    """Seconds since the named snapshot file in the data dir was last written,
    or None if it doesn't exist. `now` is passed in (caller owns the clock)."""
    path = data_dir() / name
    try:
        return max(0.0, now - path.stat().st_mtime)
    except OSError:
        return None
