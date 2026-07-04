"""Currency of a yfinance price series + sub-unit normalization, for EUR conversion.

Yahoo quotes each instrument in its listing currency (USD for US, EUR for Xetra,
JPY for Tokyo, …) — and, crucially, in *minor units* for a few markets: London
(`.L`) is pence (GBp), not pounds. Getting that wrong is a silent 100× error.

We resolve the currency from the yfinance suffix (deterministic for our universe)
and expose normalize() to convert a minor-unit quote into its major unit before
applying an FX rate. Volume: for stocks/ETFs it's a share COUNT (convert turnover
= price×shares); for crypto Yahoo reports it as quote-currency (USD) notional.
"""

from __future__ import annotations

# yfinance market suffix -> ISO currency (as Yahoo quotes it; GBp = pence).
SUFFIX_CCY = {
    "L": "GBp",
    "DE": "EUR",
    "PA": "EUR",
    "AS": "EUR",
    "BR": "EUR",
    "LS": "EUR",
    "MI": "EUR",
    "MC": "EUR",
    "HE": "EUR",
    "IR": "EUR",
    "AT": "EUR",
    "VI": "EUR",
    "SW": "CHF",
    "T": "JPY",
    "HK": "HKD",
    "TO": "CAD",
    "OL": "NOK",
    "ST": "SEK",
    "CO": "DKK",
    "SR": "SAR",
    "AX": "AUD",
    "WA": "PLN",
    "PR": "CZK",
    "BD": "HUF",
    "SI": "SGD",
    "NZ": "NZD",
    "JO": "ZAc",
    "MX": "MXN",
    "IS": "TRY",
}
# Minor-unit currencies -> (major currency, minor-per-major).
_SUBUNIT = {"GBp": ("GBP", 100.0), "ZAc": ("ZAR", 100.0), "ILA": ("ILS", 100.0)}


def currency_for(yf_ticker: str | None, status: str | None) -> str | None:
    """Listing currency of a yfinance ticker, or None if unknown."""
    if not yf_ticker:
        return None
    if status == "crypto":
        return "USD"  # BASE-USD
    if status == "forex":
        return None  # =X pairs aren't a single-currency series
    if "." in yf_ticker:
        return SUFFIX_CCY.get(yf_ticker.rsplit(".", 1)[1])
    return "USD"  # US listing (incl. class shares like BRK-B)


def normalize(ccy: str) -> tuple[str, float]:
    """(major_currency, factor): quote_in_major = quote / factor. Non-minor → (ccy, 1)."""
    return _SUBUNIT.get(ccy, (ccy, 1.0))


def is_notional_volume(status: str | None) -> bool:
    """True when Yahoo's volume is already a currency notional (crypto) rather
    than a share count (stocks/ETFs)."""
    return status == "crypto"
