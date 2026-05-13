"""Tests for the target-portfolio fetcher."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest

from ibkr_portfolio_connect.target import TargetFetchError, fetch_target_portfolio

URL = "https://example.invalid/target.json"


def _valid_body() -> dict[str, object]:
    return {
        "schema_version": 1,
        "generated_at": "2026-05-12T12:00:00Z",
        "base_currency": "USD",
        "cash_buffer_pct": 0.5,
        "positions": [
            {"symbol": "VTI", "exchange": "ARCA", "asset_class": "STK", "weight_pct": 60.0},
            {"symbol": "VXUS", "exchange": "NASDAQ", "asset_class": "STK", "weight_pct": 30.0},
            {"symbol": "BND", "exchange": "NASDAQ", "asset_class": "STK", "weight_pct": 9.5},
        ],
    }


def _transport(handler: object) -> httpx.MockTransport:
    return httpx.MockTransport(handler)  # type: ignore[arg-type]


def test_fetch_ok() -> None:
    captured: dict[str, object] = {}

    def handle(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["accept"] = request.headers.get("Accept")
        captured["auth"] = request.headers.get("Authorization")
        return httpx.Response(200, json=_valid_body())

    target = fetch_target_portfolio(URL, transport=_transport(handle))
    assert target.schema_version == 1
    assert target.cash_buffer_pct == Decimal("0.5")
    assert target.generated_at == datetime(2026, 5, 12, 12, 0, 0, tzinfo=UTC)
    assert captured["url"] == URL
    assert captured["accept"] == "application/json"
    assert captured["auth"] is None  # no token => no header


def test_fetch_with_bearer_token() -> None:
    captured: dict[str, str | None] = {}

    def handle(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("Authorization")
        return httpx.Response(200, json=_valid_body())

    fetch_target_portfolio(URL, bearer_token="abc123", transport=_transport(handle))
    assert captured["auth"] == "Bearer abc123"


def test_fetch_404() -> None:
    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="not found")

    with pytest.raises(TargetFetchError, match="HTTP 404"):
        fetch_target_portfolio(URL, transport=_transport(handle))


def test_fetch_500() -> None:
    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="upstream broken")

    with pytest.raises(TargetFetchError, match="HTTP 500"):
        fetch_target_portfolio(URL, transport=_transport(handle))


def test_fetch_empty_body() -> None:
    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"")

    with pytest.raises(TargetFetchError, match="empty response"):
        fetch_target_portfolio(URL, transport=_transport(handle))


def test_fetch_bad_schema() -> None:
    body = _valid_body()
    body["base_currency"] = "EUR"

    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    with pytest.raises(TargetFetchError, match="schema validation"):
        fetch_target_portfolio(URL, transport=_transport(handle))


def test_fetch_malformed_json() -> None:
    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, content=b"{not valid json", headers={"Content-Type": "application/json"}
        )

    with pytest.raises(TargetFetchError):
        fetch_target_portfolio(URL, transport=_transport(handle))


def test_fetch_weights_not_summing() -> None:
    body = _valid_body()
    body["cash_buffer_pct"] = 5.0  # sum becomes 104.5

    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    with pytest.raises(TargetFetchError, match="schema validation"):
        fetch_target_portfolio(URL, transport=_transport(handle))


def test_fetch_network_error() -> None:
    def handle(_r: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("could not connect")

    with pytest.raises(TargetFetchError, match="network error"):
        fetch_target_portfolio(URL, transport=_transport(handle))


def test_canonical_example_file_validates() -> None:
    """The example file shipped in the repo is itself valid against the schema."""
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / "examples" / "target-portfolio.example.json"
    body = json.loads(example.read_text())

    def handle(_r: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    target = fetch_target_portfolio(URL, transport=_transport(handle))
    assert target.schema_version == 1
    assert len(target.positions) >= 1
