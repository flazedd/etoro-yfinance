"""Tests for IBKRClient pure helpers and reply parsing.

The HTTP-layer tests that used to live here (httpx.MockTransport against the
local IBeam gateway) are gone — we now go through IBind+OAuth and trust
IBind's own test coverage for the wire format. What's left are tests for the
small bits of logic we still own: JSON→domain conversion and reply parsing.

End-to-end orchestration is exercised by test_pipeline.py via a mocked
IBKRClient.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ibkr_portfolio_connect.ibkr_client import (
    IBKRError,
    PlaceOrderReply,
    _parse_order_reply_list,
    _to_current_position,
)


class TestToCurrentPosition:
    def test_normalizes_missing_fields(self) -> None:
        raw = {"conid": 1, "position": 2.0}
        p = _to_current_position(raw)
        assert p.conid == 1
        assert p.quantity == Decimal("2.0")
        assert p.symbol == "1"  # falls back to conid
        assert p.currency == "USD"
        assert p.asset_class == "STK"
        assert p.market_value == Decimal("0")
        assert p.mkt_price is None

    def test_preserves_signed_quantity_and_value(self) -> None:
        raw = {
            "conid": 42,
            "ticker": "FOO",
            "position": -10.0,
            "mktValue": -1234.56,
            "mktPrice": 123.456,
            "currency": "EUR",
            "assetClass": "STK",
        }
        p = _to_current_position(raw)
        assert p.symbol == "FOO"
        assert p.quantity == Decimal("-10.0")
        assert p.market_value == Decimal("-1234.56")
        assert p.mkt_price == Decimal("123.456")
        assert p.currency == "EUR"

    def test_prefers_contract_desc_over_ticker(self) -> None:
        raw = {"conid": 7, "contractDesc": "Acme Inc.", "ticker": "ACME", "position": 1}
        assert _to_current_position(raw).symbol == "Acme Inc."


class TestParseOrderReplyList:
    def test_none_returns_empty(self) -> None:
        assert _parse_order_reply_list(None) == []

    def test_single_dict_wrapped_into_list(self) -> None:
        replies = _parse_order_reply_list({"order_id": "abc", "order_status": "Submitted"})
        assert len(replies) == 1
        assert replies[0].kind == "confirmed"
        assert replies[0].order_id == "abc"

    def test_list_passthrough(self) -> None:
        replies = _parse_order_reply_list([{"order_id": "1"}, {"id": "r1", "message": ["warn"]}])
        assert len(replies) == 2
        assert replies[0].kind == "confirmed"
        assert replies[1].kind == "reply_required"

    def test_unexpected_shape_raises(self) -> None:
        with pytest.raises(IBKRError, match="unexpected order reply shape"):
            _parse_order_reply_list(42)


class TestPlaceOrderReplyKind:
    def test_error_kind(self) -> None:
        assert PlaceOrderReply(error="bad").kind == "error"

    def test_reply_required_needs_both_id_and_message(self) -> None:
        assert PlaceOrderReply(id="r", message=["q"]).kind == "reply_required"
        # id without message is unknown — IBKR would never emit this.
        assert PlaceOrderReply(id="r").kind == "unknown"

    def test_confirmed_kind(self) -> None:
        assert PlaceOrderReply(order_id="o1").kind == "confirmed"

    def test_empty_is_unknown(self) -> None:
        assert PlaceOrderReply().kind == "unknown"
