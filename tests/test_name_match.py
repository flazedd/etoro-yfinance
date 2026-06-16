"""Tests for company-name similarity used to verify bbterminal->IBKR mappings."""

from __future__ import annotations

from ibkr_portfolio_connect.name_match import normalize, similarity


def test_normalize_strips_punct_and_accents() -> None:
    assert normalize("L'Oréal S.A.") == "L OREAL S A"
    assert normalize("AT&T Inc.") == "AT AND T INC"


def test_same_company_despite_legal_form_and_adr() -> None:
    # The IBKR name carries extra boilerplate; still the same company.
    assert similarity("Diageo PLC (ADR)", "DIAGEO PLC-SPONSORED ADR") >= 0.9
    assert similarity("Dongyue Group Ltd", "DONGYUE GROUP") >= 0.9
    assert similarity("Roche Holding AG", "ROCHE HLDG") >= 0.8


def test_wrong_company_traps_score_low() -> None:
    # The exact mismatches the review caught — must NOT look like a match.
    assert similarity("SM Investments Corp", "SM ENERGY CO") < 0.5
    assert similarity("LTIMindtree Ltd", "LATAM AIRLINES GROUP SA-ADR") < 0.4
    assert similarity("Hindustan Aeronautics Ltd", "HAL TRUST") < 0.4


def test_unrelated_names_score_near_zero() -> None:
    assert similarity("Apple Inc", "Banco Santander SA") < 0.3
