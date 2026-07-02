"""Resolve a bbterminal holding (ticker + exchange + currency) to an IBKR conid.

bbterminal labels listings with MIC-ish codes (XPAR, XAMS, HKSE, TSE-for-Tokyo);
IBKR labels the same listings with its own codes (SBF, AEB, SEHK, TSEJ). A naive
`secdef/search` by symbol is dangerous: the same ticker often matches a *different
company* on a US/other venue (e.g. "UMI" matches an ARCA name as well as Umicore
on Brussels). So we resolve by matching the IBKR row's listing exchange — exposed
as the row's `description` field — against the IBKR exchange(s) we expect for the
holding's bbterminal exchange, and require a STK section.

Reference data only; this never touches an account, so it works under any OAuth
session (paper or live).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from . import name_match

# IBKR listing-exchange codes that count as a US (SMART-routable, liquid) venue.
# Used to pick a preferred listing when an ETF is available on several.
_US_LISTINGS = {"ARCA", "NASDAQ", "NYSE", "BATS", "AMEX", "PINK", "IEX"}
# Name-similarity floor for a confident ticker-search ETF match (fallback path).
_ETF_NAME_OK = 0.55

# bbterminal exchange code -> acceptable IBKR listing-exchange codes (the
# `description` field of a secdef/search row) for the STK contract we want.
# Derived empirically from resolving strategy #14's 24 holdings against IBKR.
BBTERMINAL_TO_IBKR_LISTING: dict[str, set[str]] = {
    # Generic US — bbterminal says "NYSE" for any US listing; IBKR lists the
    # real primary (NYSE/NASDAQ/AMEX/ARCA). Route SMART.
    "NYSE": {"NYSE", "NASDAQ", "AMEX", "ARCA", "BATS", "PINK", "VALUE"},
    "NASDAQ": {"NYSE", "NASDAQ", "AMEX", "ARCA", "BATS", "PINK", "VALUE"},
    "TSE": {"TSEJ"},  # Tokyo Stock Exchange
    "XPAR": {"SBF"},  # Euronext Paris
    "XAMS": {"AEB"},  # Euronext Amsterdam
    "XBRU": {"ENEXT.BE"},  # Euronext Brussels
    "MIL": {"BVME"},  # Borsa Italiana (Milan)
    "OSL": {"OSE"},  # Oslo Bors
    "XSWX": {"EBS"},  # SIX Swiss Exchange
    "XKRX": {"KRX", "KSE"},  # Korea Exchange
    "HKSE": {"SEHK"},  # Hong Kong (SEHK)
    # Added from the LEONTEQ universe sweep (scripts/resolve_universe.py): the
    # home-market IBKR listing code for each exchange, confirmed present on the
    # ISIN search for ~all members. NSE (India), PHS (Manila) and DUB (Dublin)
    # are deliberately NOT here — IBKR only exposes ADR/foreign lines for those
    # ISINs, no directly-tradeable local listing, so they must stay unresolved.
    "XTER": {"IBIS"},  # Xetra (Deutsche Börse). FWB (Frankfurt floor) omitted on purpose — far less liquid.
    "LSE": {"LSE"},  # London Stock Exchange
    "TSX": {"TSE"},  # Toronto Stock Exchange (IBKR calls it TSE)
    "OSTO": {"SFB"},  # Nasdaq Stockholm
    "OCSE": {"CPH"},  # Nasdaq Copenhagen
    "OHEL": {"HEX"},  # Nasdaq Helsinki
    "XMAD": {"BM"},  # Bolsa de Madrid
    "SGX": {"SGX"},  # Singapore Exchange
    "ASX": {"ASX"},  # Australian Securities Exchange
    "XLIS": {"BVL"},  # Euronext Lisbon
    "WBO": {"VSE"},  # Wiener Börse (Vienna)
    "XPRA": {"PRA", "VSE"},  # Prague; some bbterminal XPRA names are Vienna-listed (VSE)
    "TPE": {"TWSE"},  # Taiwan Stock Exchange
}

# Exchanges whose tickers are zero-padded numbers in bbterminal but unpadded in
# IBKR (e.g. HK "02338" -> "2338"). Korea keeps its leading zeros, so it is NOT
# in this set.
_STRIP_LEADING_ZERO_EXCHANGES = {"HKSE"}

# Manual (ticker, bbterminal_exchange) -> IBKR symbol overrides. IBKR appends a
# digit when a symbol collides with another listing (e.g. the Dutch "CSG NV"
# trades as "CSG1" on AEB because "CSG" is taken by COSIGO/CMS). A plain ticker
# search can't find these, so map them explicitly. Keys are upper-cased.
SYMBOL_OVERRIDES: dict[tuple[str, str], str] = {
    ("CSG", "XAMS"): "CSG1",  # CSG NV (Euronext Amsterdam), conid 848752492
}

# Manual (ticker, bbterminal_exchange) -> pinned IBKR contract. Last resort for
# names where neither ISIN nor ticker search lands on a tradeable listing on the
# bbterminal-labelled exchange — typically because bbterminal mislabels the venue
# (an ADR tagged to a local exchange, a US stock tagged to its thin German line,
# an HK name tagged XTER). We pin the verified IBKR contract for the SAME company
# directly, bypassing exchange-matching. Each entry is a deliberate, reviewed
# substitution; `git blame` is the audit trail. Values: (conid, ibkr_symbol,
# ibkr_listing). Keys are upper-cased (ticker, bbterminal_exchange).
CONID_OVERRIDES: dict[tuple[str, str], tuple[int, str, str]] = {
    # --- LEONTEQ universe, reviewed 2026-06-16 (scripts/inspect_candidates.py) ---
    # ADRs that bbterminal tags to a local exchange; the ISIN is the US line, so
    # we pin the US-listed ADR (the instrument bbterminal actually prices).
    ("DGED", "LSE"): (7788, "DEO", "NYSE"),  # Diageo plc ADR
    ("0HKP", "LSE"): (5171, "BP", "NYSE"),  # BP plc ADR
    ("0ADF", "LSE"): (653400472, "ARM", "NYSE"),  # Arm Holdings ADR
    ("YPF", "XTER"): (14019, "YPF", "NYSE"),  # YPF SA ADR
    ("BVXB", "XTER"): (58996617, "ITUB", "NYSE"),  # Itau Unibanco ADR
    ("22UA", "XTER"): (386752917, "BNTX", "NYSE"),  # BioNTech SE ADR
    ("CLV", "XTER"): (390332321, "TCOM", "NYSE"),  # Trip.com Group ADR
    ("N1UA", "XTER"): (554208336, "EDU", "NYSE"),  # New Oriental Education ADR
    ("INFY", "NSE"): (4813460, "INFY", "NYSE"),  # Infosys ADR (NSE India not directly tradeable)
    ("RYA", "DUB"): (210918190, "RYAAY", "NYSE"),  # Ryanair Holdings ADR
    # Bermuda-incorporated, primary US listing; bbterminal tags its thin German line.
    ("SZ2", "XTER"): (53747825, "SIG", "NYSE"),  # Signet Jewelers Ltd
    # HK names mis-tagged XTER; pin the SEHK main-board (HKD) listing.
    ("CTM", "XTER"): (3408229, "941", "SEHK"),  # China Mobile Ltd (00941.HK)
    ("SHX", "XTER"): (46636743, "1071", "SEHK"),  # Huadian Power Intl H (01071.HK)
    # TSMC tagged TSE/JPY but its ISIN (US8740391003) is the US ADR. The ISIN->
    # ticker fallback wrongly matched Japanese ticker 2330 (Forside Co Ltd) on
    # TSEJ — a different company the name-verify caught. Pin the TSM ADR.
    ("2330", "TSE"): (6223250, "TSM", "NYSE"),  # Taiwan Semiconductor ADR
    # --- LEONTEQ universe #15 refresh, reviewed 2026-06-17 ---
    # bbterminal now tags QinetiQ as its thin US OTC-pink ADR (OTCPK/USD). The
    # ISIN lists on LSE too; trade the liquid London primary (GBP) instead.
    ("QNTQF", "OTCPK"): (37920799, "QQ.", "LSE"),  # QinetiQ Group plc, LSE primary
}


class ResolvedContract(BaseModel):
    ticker: str
    bbterminal_exchange: str
    currency: str
    conid: int
    ibkr_listing: str
    ibkr_symbol: str
    routing_exchanges: list[str]
    method: str = "ticker"  # "isin" (preferred) or "ticker" (fallback)


class ContractResolutionError(Exception):
    """No acceptable STK contract for this holding on IBKR."""


def _candidate_symbols(ticker: str, bbterminal_exchange: str) -> list[str]:
    """Symbol spellings to try, in order: an explicit IBKR-rename override
    first, then the raw ticker, then a leading-zero-stripped variant where the
    exchange needs it."""
    exch = bbterminal_exchange.upper()
    out: list[str] = []
    override = SYMBOL_OVERRIDES.get((ticker.upper(), exch))
    if override:
        out.append(override)
    if ticker not in out:
        out.append(ticker)
    if exch in _STRIP_LEADING_ZERO_EXCHANGES and ticker.isdigit():
        stripped = ticker.lstrip("0") or "0"
        if stripped not in out:
            out.append(stripped)
    return out


def _row_exchanges(row: dict[str, Any]) -> list[str]:
    """All routing exchanges listed across a row's sections."""
    exchanges: list[str] = []
    for sec in row.get("sections") or []:
        ex = str(sec.get("exchange", "") or "")
        for part in ex.replace(",", ";").split(";"):
            part = part.strip()
            if part and part not in exchanges:
                exchanges.append(part)
    return exchanges


def _row_has_stk(row: dict[str, Any]) -> bool:
    return any(
        str(sec.get("secType", "")).upper() == "STK" for sec in row.get("sections") or []
    )


def _accepted_listings(bbterminal_exchange: str) -> set[str]:
    accepted = BBTERMINAL_TO_IBKR_LISTING.get(bbterminal_exchange.upper())
    if accepted is None:
        raise ContractResolutionError(
            f"no IBKR exchange mapping for bbterminal exchange {bbterminal_exchange!r}; "
            "add it to BBTERMINAL_TO_IBKR_LISTING"
        )
    return accepted


def _parse_isin_row(row: dict[str, Any]) -> tuple[int, str, str] | None:
    """An ISIN-search row -> (conid, ibkr_symbol, exchange), or None if unparsable.

    ISIN rows look like: conid="291956769" or "291956769@FWB",
    companyName="UMI STK@FWB". The integer before "@" is the orderable conid;
    the venue after the final "@" in companyName is the listing/routing exchange.
    """
    raw_conid = str(row.get("conid") or "")
    name = str(row.get("companyName") or row.get("companyHeader") or "").strip()
    if not raw_conid or "@" not in name:
        return None
    try:
        conid = int(raw_conid.split("@", 1)[0])
    except ValueError:
        return None
    symbol = name.split(" ", 1)[0].strip()
    exchange = name.rsplit("@", 1)[-1].strip().upper()
    return conid, symbol, exchange


def resolve_by_isin(
    client: Any, isin: str, bbterminal_exchange: str, currency: str, *, ticker: str = ""
) -> ResolvedContract:
    """Resolve via ISIN — collision-free, so it never returns a different
    company. Picks the row whose listing exchange matches the holding's
    bbterminal exchange. Raises if IBKR has no listing on that exchange.
    """
    accepted = _accepted_listings(bbterminal_exchange)
    rows = client.secdef_search_raw(isin)
    seen_exchanges: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        parsed = _parse_isin_row(row)
        if parsed is None:
            continue
        conid, symbol, exchange = parsed
        seen_exchanges.append(exchange)
        if exchange in accepted:
            return ResolvedContract(
                ticker=ticker,
                bbterminal_exchange=bbterminal_exchange,
                currency=currency,
                conid=conid,
                ibkr_listing=exchange,
                ibkr_symbol=symbol,
                routing_exchanges=sorted(set(seen_exchanges)),
                method="isin",
            )
    raise ContractResolutionError(
        f"ISIN {isin} has no IBKR listing on {sorted(accepted)} "
        f"({bbterminal_exchange}); venues seen: {sorted(set(seen_exchanges))}"
    )


def resolve_by_ticker(client: Any, ticker: str, bbterminal_exchange: str, currency: str) -> ResolvedContract:
    """Resolve by symbol search, matching the IBKR listing-exchange code carried
    in each row's `description` and requiring a STK section — so we never
    silently pick a same-ticker company on the wrong venue. Used as a fallback
    when no ISIN is available."""
    accepted = _accepted_listings(bbterminal_exchange)
    tried: list[str] = []
    for symbol in _candidate_symbols(ticker, bbterminal_exchange):
        rows = client.secdef_search_raw(symbol)
        tried.append(symbol)
        for row in rows:
            if not isinstance(row, dict) or row.get("symbol") is None:
                continue
            listing = str(row.get("description") or "").strip().upper()
            if listing in accepted and _row_has_stk(row):
                return ResolvedContract(
                    ticker=ticker,
                    bbterminal_exchange=bbterminal_exchange,
                    currency=currency,
                    conid=int(row["conid"]),
                    ibkr_listing=listing,
                    ibkr_symbol=str(row.get("symbol")),
                    routing_exchanges=_row_exchanges(row),
                    method="ticker",
                )
    raise ContractResolutionError(
        f"no STK on {sorted(accepted)} for {ticker!r} ({bbterminal_exchange}); "
        f"tried symbols {tried}"
    )


def resolve_contract(
    client: Any,
    ticker: str,
    bbterminal_exchange: str,
    currency: str,
    isin: str | None = None,
) -> ResolvedContract:
    """Resolve one holding to a single IBKR STK conid, or raise.

    A reviewed CONID_OVERRIDES pin wins outright; otherwise prefer ISIN
    (collision-free) when available, falling back to ticker+exchange symbol
    search. `client` must expose `secdef_search_raw(symbol) -> list[dict]`.
    """
    override = CONID_OVERRIDES.get((ticker.upper(), bbterminal_exchange.upper()))
    if override:
        conid, ibkr_symbol, ibkr_listing = override
        return ResolvedContract(
            ticker=ticker,
            bbterminal_exchange=bbterminal_exchange,
            currency=currency,
            conid=conid,
            ibkr_listing=ibkr_listing,
            ibkr_symbol=ibkr_symbol,
            routing_exchanges=[ibkr_listing],
            method="override",
        )
    if isin:
        try:
            return resolve_by_isin(client, isin, bbterminal_exchange, currency, ticker=ticker)
        except ContractResolutionError:
            # ISIN unknown to IBKR (e.g. very new listing) — fall back to ticker.
            pass
    return resolve_by_ticker(client, ticker, bbterminal_exchange, currency)


# ─── ETF tradability ─────────────────────────────────────────────────────────
# ETFs (bbterminal benchmarks with an ISIN) carry NO exchange/country, so the
# exchange-matching path above doesn't apply. We only want to know: does IBKR
# list this ISIN anywhere, and where? ISIN search is collision-free (an ISIN
# names exactly one instrument), so a hit is a real, tradeable listing of that
# fund; ticker search is a lower-confidence fallback guarded by a name match.


class ETFTradability(BaseModel):
    isin: str
    tradable: bool
    conid: int | None = None
    ibkr_symbol: str | None = None
    ibkr_name: str | None = None
    ibkr_listings: list[str] = []  # every venue IBKR lists this instrument on
    preferred_listing: str | None = None  # a US venue if present, else the first
    method: str = "none"  # "isin" (preferred) | "ticker" (fallback) | "none"
    name_score: float | None = None  # only set on the ticker fallback


def _ibkr_header_name(row: dict[str, Any]) -> str:
    """`companyHeader` is 'INVESCO S&P 500 MOMENTUM ETF - ARCA'; drop the venue."""
    header = str(row.get("companyHeader") or row.get("companyName") or "")
    return header.rsplit(" - ", 1)[0].strip() if " - " in header else header


def resolve_etf_tradability(
    client: Any, isin: str, *, ticker: str = "", name: str = ""
) -> ETFTradability:
    """Is this ETF tradeable on IBKR? ISIN-first (collision-free), with a
    name-guarded ticker-search fallback for the rare ISIN IBKR doesn't index.

    `client` must expose `secdef_search_raw(query) -> list[dict]`. Never raises
    for a not-found instrument — returns `tradable=False, method="none"`.
    """
    # ISIN-first: every parseable row is a venue for the SAME instrument.
    listings: list[tuple[int, str, str]] = []
    if isin:
        for row in client.secdef_search_raw(isin):
            if not isinstance(row, dict):
                continue
            parsed = _parse_isin_row(row)
            if parsed is not None:
                listings.append(parsed)
    if listings:
        venues = sorted({venue for _, _, venue in listings})
        # Prefer a US listing (SMART-routable, liquid) when the fund lists on
        # several; otherwise take the first venue IBKR returned.
        conid, symbol, venue = next(
            (lst for lst in listings if lst[2] in _US_LISTINGS), listings[0]
        )
        return ETFTradability(
            isin=isin, tradable=True, conid=conid, ibkr_symbol=symbol,
            ibkr_listings=venues, preferred_listing=venue, method="isin",
        )

    # Fallback: symbol search + name match (lower confidence — a bare ticker can
    # match a different fund, so only trust it when the name lines up).
    if ticker:
        best: tuple[float, bool, dict[str, Any]] | None = None
        for row in client.secdef_search_raw(ticker):
            if not isinstance(row, dict) or row.get("symbol") is None:
                continue
            if not _row_has_stk(row):
                continue
            listing = str(row.get("description") or "").upper()
            score = name_match.similarity(name, _ibkr_header_name(row)) if name else 0.0
            key = (score, listing in _US_LISTINGS, row)
            if best is None or key[:2] > best[:2]:
                best = key
        if best is not None and best[0] >= _ETF_NAME_OK:
            score, _, row = best
            listing = str(row.get("description") or "").upper()
            return ETFTradability(
                isin=isin, tradable=True, conid=int(row["conid"]),
                ibkr_symbol=str(row.get("symbol")), ibkr_name=_ibkr_header_name(row),
                ibkr_listings=[listing] if listing else [], preferred_listing=listing or None,
                method="ticker", name_score=round(score, 3),
            )

    return ETFTradability(isin=isin, tradable=False, method="none")
