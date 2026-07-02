"""Tests for the unified LEONTEQ+ETF -> IBKR mapping publisher.

Fakes stand in for both the bbterminal client and the IBKR client so we can
exercise the resolution loop — the brokerage-session priming, the "no bridge"
re-init + retry recovery, genuine-no-listing classification, and ETF resolution
— without any network.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ibkr_portfolio_connect import mapping_snapshot as mapmod
from ibkr_portfolio_connect.ibkr_client import IBKRError


class FakeBB:
    def universes(self, include_all: bool = False) -> list[dict[str, Any]]:
        return [{"universe_id": 15, "label": "LEONTEQ (as of 2026-06-17)", "as_of_date": "2026-06-17"}]

    def universe(self, uid: int) -> dict[str, Any]:
        return {"members": [
            {"company_id": 1, "ticker": "AA", "exchange": "NYSE", "country": "United States",
             "currency": "USD", "isin": "US_AA", "company_name": "Alcoa"},
            # XLON isn't in the IBKR exchange map -> a genuine resolution error.
            {"company_id": 2, "ticker": "FOO", "exchange": "XLON", "country": "UK",
             "currency": "GBP", "isin": "GB_FOO", "company_name": "Foo plc"},
        ]}

    def etfs(self) -> list[dict[str, Any]]:
        return [{"benchmark_id": -1, "ticker": "SPMO", "isin": "US_SPMO",
                 "name": "Invesco Momentum ETF", "currency": "USD", "sector": "ETF"}]


class FakeIBKR:
    """Simulates the brokerage session dropping once on the first equity lookup."""

    def __init__(self) -> None:
        self.init_calls = 0
        self.dropped_once = False

    def init_brokerage_session(self) -> None:
        self.init_calls += 1

    def tickle(self) -> dict[str, Any]:
        return {}

    def secdef_search_raw(self, query: str) -> list[dict[str, Any]]:
        if query == "US_AA" and not self.dropped_once:
            self.dropped_once = True
            raise IBKRError("secdef_search(US_AA): IBKR returned 400 Bad Request: no bridge")
        rows = {
            "US_AA": [{"conid": "111@NYSE", "companyName": "AA STK@NYSE"}],
            "US_SPMO": [{"conid": "222@ARCA", "companyName": "SPMO STK@ARCA"}],
        }
        return rows.get(query, [])


def test_build_snapshot_recovers_session_and_classifies(tmp_path: Path) -> None:
    bb, ibkr = FakeBB(), FakeIBKR()
    snap = mapmod.build_snapshot(bb, ibkr, data_dir=tmp_path, throttle=0.0)

    # session primed once up front + re-initialized once on the 'no bridge' drop
    assert ibkr.init_calls == 2

    rows = {r["ticker"]: r for r in snap["rows"]}
    assert rows["AA"]["status"] == "resolved"      # recovered after the retry
    assert rows["AA"]["conid"] == 111
    assert rows["AA"]["method"] == "isin"
    assert rows["FOO"]["status"] == "error"        # genuine: no IBKR exchange mapping
    assert rows["FOO"]["method"] == "none"
    assert "exchange mapping" in rows["FOO"]["note"]
    assert rows["SPMO"]["kind"] == "etf"
    assert rows["SPMO"]["status"] == "resolved"
    assert rows["SPMO"]["conid"] == 222

    assert snap["counts"] == {"total": 3, "equities": 2, "etfs": 1,
                              "tradable": 2, "unresolved": 1, "retryable": 0}
    assert snap["universe_id"] == 15


def test_persistent_session_error_is_reported_not_raised(tmp_path: Path) -> None:
    class AlwaysNoBridge(FakeIBKR):
        def secdef_search_raw(self, query: str) -> list[dict[str, Any]]:
            raise IBKRError("secdef_search: IBKR returned 400 Bad Request: no bridge")

    snap = mapmod.build_snapshot(FakeBB(), AlwaysNoBridge(), data_dir=tmp_path, throttle=0.0)
    aa = next(r for r in snap["rows"] if r["ticker"] == "AA")
    assert aa["status"] == "error"
    assert aa["method"] == "error"
    # a persistent session error is counted so the page can prompt a re-run
    assert snap["counts"]["retryable"] >= 1


def test_discover_universe_env_override(monkeypatch: Any) -> None:
    monkeypatch.setenv("MAPPING_UNIVERSE_ID", "42")
    assert mapmod.discover_universe(FakeBB()) == (42, "")
