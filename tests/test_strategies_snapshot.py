"""Tests for the scheduled-strategies snapshot builder + web enrichment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ibkr_portfolio_connect import strategies_snapshot as ss
from ibkr_portfolio_connect.web.server import _enrich_strategies


class _FakeBB:
    """Two enabled strategies; #30's performance endpoint is down (young)."""

    def __init__(self) -> None:
        self.perf_calls = 0

    def schedules(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        assert enabled_only is True
        return [{"strategy_id": 28, "name": "Offensief"},
                {"strategy_id": 30, "name": "Defensief"}]

    def schedule(self, sid: int) -> dict[str, Any]:
        return {
            "name": f"Strat {sid}", "enabled": True, "frequency": "monthly",
            "next_rebalance_at": "2026-07-04T02:00:00+00:00", "as_of_date": "2026-06-23",
            "holdings_count": 1,
            "holdings": [{"company_id": 5470, "ticker": "SNDK", "isin": "US80004C2008",
                          "company_name": "SanDisk Corp", "target_weight": 0.0417,
                          "side": "long", "score": 54.94}],
        }

    def performance(self, sid: int) -> dict[str, Any]:
        self.perf_calls += 1
        if sid == 30:
            raise RuntimeError("no performance yet")
        return {"inception_date": "2026-06-29", "mtd_return_pct": 0.33,
                "since_inception_return_pct": 0.33}


def test_build_snapshot_carries_holdings_and_survives_missing_perf(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MOMENTUM_DATA_DIR", str(tmp_path))
    bb = _FakeBB()
    snap = ss.build_snapshot(bb)  # type: ignore[arg-type]

    assert snap["count"] == 2
    assert snap["enabled_only"] is True
    s28, s30 = snap["strategies"]
    assert s28["strategy_id"] == 28
    assert s28["mtd_return_pct"] == 0.33
    assert len(s28["holdings"]) == 1
    # #30's perf blew up but the strategy is still present, perf fields None.
    assert s30["strategy_id"] == 30
    assert s30["mtd_return_pct"] is None
    assert bb.perf_calls == 2

    out = ss.write_local(snap, tmp_path)
    assert json.loads(out.read_text())["strategies"][0]["name"] == "Strat 28"


def test_enrich_merges_conid_by_company_id_then_isin() -> None:
    mapping = {"rows": [
        {"company_id": 5470, "isin": "US80004C2008", "ticker": "SNDK",
         "conid": 760250490, "confidence": "high", "ibkr_symbol": "SNDK",
         "ibkr_quote_url": "http://ib/760250490", "tradable": True},
        # ETF keyed by benchmark_id (not the holding's company_id) — ISIN links it.
        {"company_id": 43, "isin": "US46138E3392", "ticker": "SPMO",
         "conid": 319357139, "confidence": "high", "tradable": True},
    ]}
    strategies = [{"strategy_id": 28, "name": "Offensief", "holdings": [
        {"company_id": 5470, "ticker": "SNDK", "isin": "US80004C2008"},
        {"company_id": -1, "ticker": "SPMO", "isin": "US46138E3392"},  # ETF via ISIN
        {"company_id": None, "ticker": "CASH", "isin": None},          # stays bare
    ]}]

    out = _enrich_strategies(strategies, mapping)
    h = out[0]["holdings"]
    assert h[0]["conid"] == 760250490
    assert h[0]["confidence"] == "high"
    assert h[1]["conid"] == 319357139          # matched by ISIN despite wrong cid
    assert h[2]["conid"] is None               # CASH unmatched
