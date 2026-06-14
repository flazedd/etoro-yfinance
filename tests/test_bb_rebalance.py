"""Tests for the bbterminal buy/replace planning logic (pure, no gateway)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ibkr_portfolio_connect.bb_rebalance import (
    RebalanceInputError,
    build_targets,
    check_strategy_freshness,
    extract_nav,
    plan_trades,
)
from ibkr_portfolio_connect.conid_map import ConidMap, ConidMapError, make_entry
from ibkr_portfolio_connect.schema import CurrentPosition, OrderSide

NOW = "2026-06-14T00:00:00+00:00"


def _holding(company_id: int, ticker: str, conid_hint: int, **over: Any) -> dict[str, Any]:
    h = {
        "company_id": company_id,
        "ticker": ticker,
        "company_name": f"{ticker} Inc",
        "isin": f"XX{company_id:010d}",
        "exchange": "NYSE",
        "currency": "USD",
        "target_weight": 0.25,
        "entry_price_eur": 100.0,
        "_conid_hint": conid_hint,
    }
    h.update(over)
    return h


def _map_with(*holdings: dict[str, Any], reviewed: bool = True) -> ConidMap:
    m = ConidMap()
    for h in holdings:
        e = make_entry(
            h,
            conid=int(h["_conid_hint"]),
            ibkr_symbol=str(h["ticker"]),
            ibkr_listing="NYSE",
            resolved_via="isin",
            reviewed=reviewed,
            now=NOW,
        )
        m.put(e)
    return m


# ---- build_targets ----------------------------------------------------------


def test_build_targets_sizes_in_eur_and_uses_reviewed_conid() -> None:
    h = _holding(1, "AAA", 111, target_weight=0.25, entry_price_eur=50.0)
    targets = build_targets([h], _map_with(h))
    assert len(targets) == 1
    t = targets[0]
    assert t.conid == 111
    assert t.weight_pct == Decimal("25.00")  # 0.25 * 100
    assert t.reference_price == Decimal("50.0")


def test_build_targets_refuses_unreviewed() -> None:
    h = _holding(1, "AAA", 111)
    with pytest.raises(ConidMapError, match="not reviewed"):
        build_targets([h], _map_with(h, reviewed=False))


def test_build_targets_refuses_missing() -> None:
    h = _holding(1, "AAA", 111)
    with pytest.raises(ConidMapError, match="not in the conid map"):
        build_targets([h], ConidMap())


def test_build_targets_detects_isin_drift() -> None:
    h = _holding(1, "AAA", 111)
    m = _map_with(h)
    drifted = {**h, "isin": "ZZ9999999999"}
    with pytest.raises(ConidMapError, match="ISIN drift"):
        build_targets([drifted], m)


# ---- plan_trades (buy/replace end to end, pure) -----------------------------


def test_plan_replaces_old_portfolio() -> None:
    # Target: two names, 25% each, €100/share, NAV €10,000 -> 25 shares each.
    new = [
        _holding(1, "NEW1", 111, target_weight=0.25, entry_price_eur=100.0),
        _holding(2, "NEW2", 222, target_weight=0.25, entry_price_eur=100.0),
    ]
    cmap = _map_with(*new)
    # Currently hold an OLD name (conid 999, not in target) + some of NEW1.
    positions = [
        CurrentPosition(conid=999, symbol="OLD", asset_class="STK", quantity=Decimal("10"),
                        market_value=Decimal("1000"), currency="USD"),
        CurrentPosition(conid=111, symbol="NEW1", asset_class="STK", quantity=Decimal("5"),
                        market_value=Decimal("500"), currency="USD"),
    ]
    trades = plan_trades(holdings=new, conid_map=cmap, positions=positions, nav=Decimal("10000"))
    by_conid = {t.conid: t for t in trades}

    # OLD fully liquidated
    assert by_conid[999].side is OrderSide.SELL
    assert by_conid[999].quantity == 10
    # NEW1: top up 5 -> 25
    assert by_conid[111].side is OrderSide.BUY
    assert by_conid[111].quantity == 20
    # NEW2: fresh 25
    assert by_conid[222].side is OrderSide.BUY
    assert by_conid[222].quantity == 25
    # sells sorted before buys
    assert trades[0].side is OrderSide.SELL


def test_plan_no_trades_when_already_aligned() -> None:
    h = _holding(1, "AAA", 111, target_weight=1.0, entry_price_eur=100.0)
    positions = [
        CurrentPosition(conid=111, symbol="AAA", asset_class="STK", quantity=Decimal("100"),
                        market_value=Decimal("10000"), currency="USD")
    ]
    trades = plan_trades(holdings=[h], conid_map=_map_with(h), positions=positions, nav=Decimal("10000"))
    assert trades == []


# ---- extract_nav ------------------------------------------------------------


def test_extract_nav_dict_with_matching_currency() -> None:
    summary = {"netliquidation": {"amount": "12345.67", "currency": "EUR"}}
    assert extract_nav(summary, required_currency="EUR") == Decimal("12345.67")


def test_extract_nav_rejects_wrong_currency() -> None:
    summary = {"netliquidation": {"amount": "12345.67", "currency": "USD"}}
    with pytest.raises(RebalanceInputError, match="does not auto-convert"):
        extract_nav(summary, required_currency="EUR")


def test_extract_nav_bare_number_trusted() -> None:
    assert extract_nav({"netliquidation": 5000}, required_currency="EUR") == Decimal("5000")


def test_extract_nav_missing_raises() -> None:
    with pytest.raises(RebalanceInputError, match="could not extract"):
        extract_nav({"foo": 1}, required_currency="EUR")


# ---- freshness --------------------------------------------------------------


def test_freshness_ok_within_window() -> None:
    check_strategy_freshness(
        {"as_of_date": "2026-06-09"}, max_age_days=14, now=date(2026, 6, 14)
    )


def test_freshness_too_old_raises() -> None:
    with pytest.raises(RebalanceInputError, match="exceeds"):
        check_strategy_freshness(
            {"as_of_date": "2026-05-01"}, max_age_days=14, now=date(2026, 6, 14)
        )


def test_freshness_disabled_when_none() -> None:
    check_strategy_freshness({"as_of_date": "2000-01-01"}, max_age_days=None)


def test_freshness_missing_as_of_raises() -> None:
    with pytest.raises(RebalanceInputError, match="no as_of_date"):
        check_strategy_freshness({}, max_age_days=14)
