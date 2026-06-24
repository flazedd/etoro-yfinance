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


def test_spacing_and_punctuation_only_difference_is_exact() -> None:
    # IBKR's security master spells McDonald's with a space ("MC DONALD'S"),
    # which used to split the key token and sink the score. The de-spaced
    # identity strings are identical, so it must read as a full match.
    assert similarity("McDonald's Corp", "MC DONALD'S-CORP") >= 0.95
    assert similarity("MC DONALD'S-CORP", "MCDONALD'S CORP") >= 0.95
    # Segmentation differences in general collapse.
    assert similarity("JPMorgan Chase & Co", "JP MORGAN CHASE & CO") >= 0.95


def test_wrong_company_traps_score_low() -> None:
    # The exact mismatches the review caught — must NOT look like a match.
    assert similarity("SM Investments Corp", "SM ENERGY CO") < 0.5
    assert similarity("LTIMindtree Ltd", "LATAM AIRLINES GROUP SA-ADR") < 0.4
    assert similarity("Hindustan Aeronautics Ltd", "HAL TRUST") < 0.4


def test_unrelated_names_score_near_zero() -> None:
    assert similarity("Apple Inc", "Banco Santander SA") < 0.3
