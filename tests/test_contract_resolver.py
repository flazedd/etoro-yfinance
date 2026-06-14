"""Tests for the bbterminal-holding -> IBKR-conid resolver.

These use a fake client returning canned secdef/search rows shaped like the
real IBKR responses we observed for strategy #14, so we exercise the matching
logic (listing-exchange match, STK requirement, leading-zero handling, wrong-
venue rejection) without touching the network.
"""

from __future__ import annotations

from typing import Any

import pytest

from ibkr_portfolio_connect.contract_resolver import (
    ContractResolutionError,
    resolve_by_isin,
    resolve_contract,
)

Row = dict[str, Any]


class FakeClient:
    """Returns canned rows keyed by the searched symbol."""

    def __init__(self, by_symbol: dict[str, list[Row]]) -> None:
        self._by_symbol = by_symbol
        self.searched: list[str] = []

    def secdef_search_raw(self, symbol: str) -> list[Row]:
        self.searched.append(symbol)
        return self._by_symbol.get(symbol, [])


def _row(conid: int, symbol: str | None, listing: str | None, *, stk: bool = True, exch: str = "SMART") -> Row:
    sections = [{"secType": "STK", "exchange": exch}] if stk else [{"secType": "OPT", "exchange": exch}]
    return {"conid": conid, "symbol": symbol, "description": listing, "sections": sections}


def test_us_ticker_matches_nasdaq() -> None:
    client = FakeClient({"AAOI": [_row(135423662, "AAOI", "NASDAQ")]})
    rc = resolve_contract(client, "AAOI", "NYSE", "USD")
    assert rc.conid == 135423662
    assert rc.ibkr_listing == "NASDAQ"


def test_picks_correct_foreign_venue_over_same_ticker_us() -> None:
    # "UMI" exists on ARCA (wrong company) and ENEXT.BE (Umicore, the one we want).
    client = FakeClient(
        {
            "UMI": [
                _row(478647421, "UMI", "ARCA"),
                _row(291956769, "UMI", "ENEXT.BE"),
            ]
        }
    )
    rc = resolve_contract(client, "UMI", "XBRU", "EUR")
    assert rc.conid == 291956769
    assert rc.ibkr_listing == "ENEXT.BE"


def test_hk_leading_zero_is_stripped() -> None:
    # Raw "02338" returns nothing; "2338" returns the SEHK listing.
    client = FakeClient({"2338": [_row(46652418, "2338", "SEHK")]})
    rc = resolve_contract(client, "02338", "HKSE", "HKD")
    assert rc.conid == 46652418
    assert client.searched == ["02338", "2338"]


def test_rejects_non_stk_match() -> None:
    client = FakeClient({"X": [_row(1, "X", "BVME", stk=False)]})
    with pytest.raises(ContractResolutionError):
        resolve_contract(client, "X", "MIL", "EUR")


def test_rejects_wrong_listing_only() -> None:
    # Only a COSIGO/CMS-style match on the wrong venue -> refuse, never guess.
    client = FakeClient({"CSG": [_row(87467563, "CSG", "VENTURE"), _row(80702143, "CSG", "FWB")]})
    with pytest.raises(ContractResolutionError):
        resolve_contract(client, "CSG", "XAMS", "EUR")


def test_symbol_override_for_ibkr_rename() -> None:
    # CSG (Amsterdam) trades as "CSG1" on IBKR; a plain "CSG" search finds the
    # wrong companies, so the override must be tried first.
    client = FakeClient(
        {
            "CSG": [_row(87467563, "CSG", "VENTURE"), _row(80702143, "CSG", "FWB")],
            "CSG1": [_row(848752492, "CSG1", "AEB")],
        }
    )
    rc = resolve_contract(client, "CSG", "XAMS", "EUR")
    assert rc.conid == 848752492
    assert rc.ibkr_symbol == "CSG1"
    assert client.searched[0] == "CSG1"  # override tried before raw ticker


def test_unmapped_exchange_raises() -> None:
    client = FakeClient({})
    with pytest.raises(ContractResolutionError, match="no IBKR exchange mapping"):
        resolve_contract(client, "FOO", "XLON", "GBP")


def test_skips_null_symbol_rows() -> None:
    client = FakeClient(
        {"F": [{"conid": 2147483647, "symbol": None, "description": None, "sections": []}, _row(9599491, "F", "NYSE")]}
    )
    rc = resolve_contract(client, "F", "NYSE", "USD")
    assert rc.conid == 9599491


# ---- ISIN resolution -------------------------------------------------------


def _isin_row(conid: str, symbol: str, exchange: str) -> Row:
    """An ISIN-search row: conid may carry an @exchange suffix; the symbol +
    venue live in companyName as '<SYM> STK@<EXCH>'."""
    return {
        "conid": conid,
        "companyName": f"{symbol} STK@{exchange}",
        "companyHeader": f"{symbol} STK@{exchange} ",
        "symbol": "STK",
        "description": None,
        "sections": [{"secType": "STK"}],
    }


def test_isin_picks_listing_on_target_exchange() -> None:
    # Umicore ISIN returns the same conid routed to many venues; pick ENEXT.BE.
    client = FakeClient(
        {
            "BE0974320526": [
                _isin_row("291956769", "UMI", "SMART"),
                _isin_row("291956769@FWB", "UMI", "FWB"),
                _isin_row("291956769@ENEXT.BE", "UMI", "ENEXT.BE"),
            ]
        }
    )
    rc = resolve_by_isin(client, "BE0974320526", "XBRU", "EUR", ticker="UMI")
    assert rc.conid == 291956769
    assert rc.ibkr_listing == "ENEXT.BE"
    assert rc.method == "isin"


def test_isin_preferred_over_ticker() -> None:
    client = FakeClient(
        {
            "NL0015073TS8": [_isin_row("848752492", "CSG1", "AEB")],
            # ticker path would find the wrong companies — must not be used
            "CSG": [_row(87467563, "CSG", "VENTURE")],
        }
    )
    rc = resolve_contract(client, "CSG", "XAMS", "EUR", isin="NL0015073TS8")
    assert rc.conid == 848752492
    assert rc.method == "isin"


def test_falls_back_to_ticker_when_isin_not_on_ibkr() -> None:
    # ISIN known to IBKR only on a non-target venue -> fall back to ticker search.
    client = FakeClient(
        {
            "XX0000000000": [_isin_row("999", "FOO", "LSE")],  # not AEB
            "FOO": [_row(123, "FOO", "AEB")],
        }
    )
    rc = resolve_contract(client, "FOO", "XAMS", "EUR", isin="XX0000000000")
    assert rc.conid == 123
    assert rc.method == "ticker"
