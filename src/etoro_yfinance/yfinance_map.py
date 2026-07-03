"""Map an eToro execution instrument → a yfinance analysis ticker.

eToro is where you trade; yfinance (Yahoo) is where the price/volume history for
analysis comes from. Yahoo is keyed by TICKER (+ a market suffix like `.L`,
`.DE`), not ISIN — and, crucially, eToro's `symbolFull` ALREADY carries the
right suffix for international names (Siemens = `SIE.DE`, Xiaomi = `1810.HK`,
Accor = `AC.PA`). So the map is mostly identity, with three wrinkles:

  - eToro's SIX-Zurich suffix is `.ZU`; Yahoo wants `.SW`.
  - US class shares: `BRK.B` (eToro) → `BRK-B` (Yahoo).
  - Crypto → `BASE-USD`; Forex → `PAIR=X`.

eToro's stock list also contains ~13% junk (numeric/`.DUP`/`.CVR`/`.IPO`/pref
artifacts) whose "suffix" is not a real market — those are left unmapped.
ISIN is not involved (eToro doesn't publish it; OpenFIGI only maps ISIN→ticker).
"""

from __future__ import annotations

import re

# Derivatives/futures venues — eToro lists dated futures (e.g. Micro Ether/XRP)
# on these; we exclude them (spot only). CME is the one seen; the rest are
# defensive. Matched on the exchange NAME, never on the instrument name ("Future"
# there is a false-positive trap — Future plc, Faraday Future, Future FinTech…).
FUTURES_EXCHANGES = {"CME", "CBOT", "NYMEX", "COMEX", "CFE", "ICE Futures"}
# Dated-contract symbol suffix: BASE.MONYY (ETH.NOV29, XRP.JAN26).
_EXPIRY_RE = re.compile(
    r"\.(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d{2}$", re.IGNORECASE)


def is_future(symbol: str | None, exchange_name: str | None) -> bool:
    """True for dated futures contracts (excluded from the spot universe)."""
    if (exchange_name or "") in FUTURES_EXCHANGES:
        return True
    return bool(_EXPIRY_RE.search(symbol or ""))


# Quote-currency codes eToro appends for non-USD-quoted crypto (fiat + crypto).
# USD is the canonical quote we keep, so it's deliberately absent.
CRYPTO_QUOTE_CODES = sorted(
    {"EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD", "CNH", "CNY",
     "BTC", "ETH", "XLM", "XRP", "LTC", "BCH", "DASH", "USDT", "BNB"},
    key=len, reverse=True)


def is_crypto_quote_dupe(symbol: str | None, crypto_symbols: set[str]) -> bool:
    """True if a crypto symbol is <BASE><QUOTE> for a non-USD quote whose BASE is
    also in the universe (e.g. BTCEUR/ETHBTC vs the canonical BTC/ETH). Used to
    drop currency/cross duplicates — we keep only the USD-quoted coin."""
    up = (symbol or "").upper()
    for q in CRYPTO_QUOTE_CODES:
        if up.endswith(q) and len(up) > len(q) and up[:-len(q)] in crypto_symbols:
            return True
    return False


# eToro instrumentTypeId (from /market-data/instrument-types).
TYPE_FOREX = 1
TYPE_COMMODITY = 2
TYPE_INDICES = 4
TYPE_STOCKS = 5
TYPE_ETF = 6
TYPE_CRYPTO = 10

# The exchange suffixes eToro actually uses in symbolFull — all valid Yahoo
# market suffixes. Anything else after a dot is an eToro artifact, not a market.
YAHOO_SUFFIXES = {
    "L", "DE", "PA", "AS", "BR", "LS", "MI", "MC", "SW", "ZU", "T", "HK", "TO",
    "OL", "ST", "CO", "HE", "SR", "AX", "VI", "WA", "PR", "BD", "IR", "SI", "NZ",
    "JO", "MX", "IS", "AT",
}
# Where eToro's suffix differs from Yahoo's.
SUFFIX_REMAP = {"ZU": "SW"}

# US exchanges — used to recognise a US class share (BRK.B → BRK-B).
US_EXCHANGES = {"Nasdaq", "NYSE", "OTC Markets Stock Exchange",
                "Chicago Board Options Exchange"}

STATUS_US = "us"
STATUS_INTL = "intl"
STATUS_CRYPTO = "crypto"
STATUS_FOREX = "forex"
STATUS_UNMAPPED = "unmapped"

MAPPED_STATUSES = (STATUS_US, STATUS_INTL, STATUS_CRYPTO, STATUS_FOREX)

# eToro display-scale suffixes on tiny-priced coins (SHIBxM = Shiba "in millions"):
# a quote-unit convention, not part of the coin — strip it to reach the real coin
# (SHIBxM -> SHIB, so the Yahoo ticker is SHIB-USD, not SHIBXM-USD).
CRYPTO_SCALE_SUFFIXES = ("xB", "xM", "xK")

# eToro coin base -> Yahoo base, where Yahoo disambiguates a reused ticker with a
# numeric suffix (the plain ticker is a different, stale coin). Applied after the
# scale strip, e.g. PEPExM -> PEPE -> PEPE24478 -> PEPE24478-USD.
CRYPTO_ALIASES = {"PEPE": "PEPE24478"}


def _norm(s: str | None) -> str:
    return " ".join((s or "").split())


def to_yfinance(*, symbol: str | None, type_id: int | None,
                exchange_name: str | None = None) -> tuple[str | None, str]:
    """Return (yahoo_ticker, status). `yahoo_ticker` is None when unmapped."""
    up = (symbol or "").strip().upper()
    if not up:
        return None, STATUS_UNMAPPED

    if type_id == TYPE_CRYPTO:
        raw = (symbol or "").strip()
        for s in CRYPTO_SCALE_SUFFIXES:            # SHIBxM -> SHIB (drop scale unit)
            if raw.endswith(s) and len(raw) > len(s):
                up = raw[:-len(s)].upper()
                break
        base = up.rsplit(".", 1)[0]
        base = CRYPTO_ALIASES.get(base, base)
        return f"{base}-USD", STATUS_CRYPTO
    if type_id == TYPE_FOREX:
        pair = up.replace("/", "").replace("-", "").rsplit(".", 1)[0]
        return f"{pair}=X", STATUS_FOREX

    if type_id in (TYPE_STOCKS, TYPE_ETF):
        if "." not in up:
            return up, STATUS_US  # plain ticker = US listing
        base, sfx = up.rsplit(".", 1)
        if sfx in YAHOO_SUFFIXES:
            ysfx = SUFFIX_REMAP.get(sfx, sfx)
            # Yahoo wants Hong Kong codes as 4-digit zero-padded (Tencent =
            # 0700.HK). eToro emits variable widths (1.HK, 101.HK, 00001.HK,
            # 03690.HK) — normalise numeric codes to ≥4 digits (5-digit HKEX
            # codes are left untouched by zfill).
            if ysfx == "HK" and base.isdigit():
                base = base.lstrip("0").zfill(4)
            return f"{base}.{ysfx}", STATUS_INTL
        if len(sfx) == 1 and sfx.isalpha() and _norm(exchange_name) in US_EXCHANGES:
            return f"{base}-{sfx}", STATUS_US  # US class share BRK.B -> BRK-B
        return None, STATUS_UNMAPPED  # numeric/.DUP/.CVR/.IPO/pref artifact

    # Indices / commodities: eToro's symbols don't line up with Yahoo's.
    return None, STATUS_UNMAPPED
