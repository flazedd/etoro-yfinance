"""Tests for the eToro-symbol → yfinance-ticker mapping (pure, no network)."""

from __future__ import annotations

import pytest

from etoro_yfinance.yfinance_map import to_yfinance


@pytest.mark.parametrize(("symbol", "type_id", "exch", "expected"), [
    ("AAPL", 5, "Nasdaq", ("AAPL", "us")),              # US stock, plain
    ("SIE.DE", 5, "FRA", ("SIE.DE", "intl")),           # symbolFull already Yahoo-shaped
    ("1810.HK", 5, "Hong Kong Exchanges", ("1810.HK", "intl")),
    ("AC.PA", 5, "Euronext Paris", ("AC.PA", "intl")),
    ("NESN.ZU", 5, "SIX", ("NESN.SW", "intl")),         # eToro .ZU -> Yahoo .SW
    ("VUSA.L", 6, "LSE", ("VUSA.L", "intl")),           # ETF
    ("BRK.B", 5, "NYSE", ("BRK-B", "us")),              # US class share
    ("BTC", 10, None, ("BTC-USD", "crypto")),
    ("ETH", 10, None, ("ETH-USD", "crypto")),
    ("EURUSD", 1, None, ("EURUSD=X", "forex")),
    ("FOO.15531", 5, "Nasdaq", (None, "unmapped")),     # junk numeric suffix, not a class share
    ("XYZ.DUP10606", 5, "LSE", (None, "unmapped")),     # eToro artifact suffix
    ("SPX500", 4, None, (None, "unmapped")),            # index — no clean Yahoo match
    ("GOLD", 2, None, (None, "unmapped")),              # commodity
    ("", 5, "Nasdaq", (None, "unmapped")),              # empty
])
def test_to_yfinance(symbol: str, type_id: int, exch: str | None,
                     expected: tuple[str | None, str]) -> None:
    assert to_yfinance(symbol=symbol, type_id=type_id, exchange_name=exch) == expected
