"""Adapter over `ibind.IbkrClient` exposing the rebalancer's IBKR surface.

We talk to IBKR via OAuth 1.0a against `api.ibkr.com` (no local gateway).
IBind handles signing + the live session token; this class normalizes the
results into our domain types and the small order-reply shape executor.py
already knows how to walk.

Tests inject a fake via `run_rebalance(..., client=<fake>)` rather than
constructing this class — production construction triggers IBind's OAuth
handshake, which requires real credentials.
"""

from __future__ import annotations

import logging
import time
from decimal import Decimal
from types import TracebackType
from typing import Any, Self

from ibind import IbkrClient as _IBind  # type: ignore[import-untyped]
from ibind.client.ibkr_utils import OrderRequest, QuestionType  # type: ignore[import-untyped]
from ibind.support.errors import ExternalBrokerError  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict

from .schema import CurrentPosition, OrderSide

log = logging.getLogger(__name__)

POSITIONS_PAGE_SIZE = 100

# secdef/search 503s intermittently on IBKR's side; how many times to try.
_SECDEF_SEARCH_ATTEMPTS = 4


class IBKRError(Exception):
    """Raised when an IBKR API call fails."""


class IBKRAuthError(IBKRError):
    """Raised when IBKR rejects us as unauthenticated/unauthorized."""


class AuthStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    authenticated: bool = False
    connected: bool = False
    competing: bool = False
    message: str = ""


class SecDefMatch(BaseModel):
    model_config = ConfigDict(extra="ignore")

    conid: int
    symbol: str
    description: str | None = None
    sections: list[dict[str, Any]] = []


class PlaceOrderReply(BaseModel):
    """One element of the response from `place_order` or `confirm_reply`.

    Three shapes share the wire format — confirmed / reply-required / rejected.
    With IBind handling the reply chain internally we will normally see only
    the `confirmed` shape, but we still parse all three so executor.py's
    chain-walker remains compatible (and `confirm_reply` works for tests).
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    order_id: str | None = None
    order_status: str | None = None
    encrypt_message: str | None = None
    id: str | None = None
    message: list[str] | None = None
    error: str | None = None

    @property
    def kind(self) -> str:
        if self.error is not None:
            return "error"
        if self.id is not None and self.message is not None:
            return "reply_required"
        if self.order_id is not None:
            return "confirmed"
        return "unknown"


# Accept every known warning automatically — this is a headless rebalancer,
# there's no human to click through dialogs. New warning types from IBKR will
# need to be added here (or detected and added) as they appear.
_AUTO_ANSWER_ALL: dict[QuestionType | str, bool] = dict.fromkeys(QuestionType, True)


class IBKRClient:
    """Synchronous client for IBKR via OAuth 1.0a (using IBind under the hood).

    Use as a context manager; IBind's OAuth shutdown runs on `close()`.
    """

    def __init__(self, *, timeout: float = 30.0) -> None:
        self._timeout = timeout
        self._ibind = _IBind(use_oauth=True, timeout=timeout)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        # IBind also registers an atexit close handler; calling explicitly is
        # safe and lets us catch errors here rather than during interpreter
        # teardown.
        try:
            self._ibind.close()
        except Exception:
            log.debug("ibind close raised; ignoring", exc_info=True)

    # ----- auth / session --------------------------------------------------

    def auth_status(self) -> AuthStatus:
        """OAuth sessions are authenticated for the life of the live session
        token (24h). If IBind's constructor succeeded, we're good.
        """
        return AuthStatus(authenticated=True, connected=True)

    def reauthenticate(self) -> None:
        """No-op under OAuth. The live session token auto-refreshes."""
        return

    def tickle(self) -> dict[str, Any]:
        try:
            return dict(self._ibind.tickle().data or {})
        except Exception as e:
            raise self._wrap(e, "tickle") from e

    def ensure_authenticated(self) -> AuthStatus:
        return self.auth_status()

    # ----- accounts --------------------------------------------------------

    def iserver_accounts(self) -> list[str]:
        """Return the list of account IDs the OAuth token can see.

        OAuth doesn't have a separate iserver/accounts session concept — the
        canonical list comes from /portfolio/accounts.
        """
        return [
            str(a.get("accountId") or a.get("id"))
            for a in self.portfolio_accounts()
            if a.get("accountId") or a.get("id")
        ]

    def portfolio_accounts(self) -> list[dict[str, Any]]:
        try:
            data = self._ibind.portfolio_accounts().data or []
            return list(data)
        except Exception as e:
            raise self._wrap(e, "portfolio_accounts") from e

    # ----- positions -------------------------------------------------------

    def positions(self, account_id: str) -> list[CurrentPosition]:
        all_raw: list[dict[str, Any]] = []
        page = 0
        while True:
            try:
                resp = self._ibind.positions(account_id=account_id, page=page)
            except Exception as e:
                raise self._wrap(e, f"positions(page={page})") from e
            data = list(resp.data or [])
            all_raw.extend(data)
            if len(data) < POSITIONS_PAGE_SIZE:
                break
            page += 1
        return [_to_current_position(item) for item in all_raw]

    # ----- symbol resolution ----------------------------------------------

    def secdef_search_raw(self, symbol: str) -> list[dict[str, Any]]:
        """Raw secdef/search rows, no validation.

        IBKR returns heterogeneous rows for a symbol search — some have a null
        `symbol` (e.g. index/derivative parents), which the strict SecDefMatch
        model rejects. Callers that just want to inspect availability across
        listings should use this and parse defensively.
        """
        # IBKR's secdef/search 503s intermittently (cold start / rate limit);
        # retry transient 503s with backoff before giving up.
        data: Any = []
        delay = 1.0
        for attempt in range(_SECDEF_SEARCH_ATTEMPTS):
            try:
                data = self._ibind.search_contract_by_symbol(symbol).data or []
                break
            except Exception as e:
                wrapped = self._wrap(e, f"secdef_search({symbol})")
                if "503" in str(e) and attempt < _SECDEF_SEARCH_ATTEMPTS - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise wrapped from e
        # IBKR usually returns a list of row dicts, but for some symbols it
        # returns a single dict or other shapes — normalize and drop non-dicts.
        if isinstance(data, dict):
            data = [data]
        return [dict(x) for x in data if isinstance(x, dict)]

    def secdef_by_conids(self, conids: list[int]) -> list[dict[str, Any]]:
        """`trsrv/secdef` for a batch of conids -> the authoritative IBKR
        name / ticker / listingExchange / currency / countryCode for each.

        Used to VERIFY a resolved conid is the company we think it is. The
        endpoint does NOT return an ISIN (the field is always null), so
        cross-check on name + currency + country instead. Batchable, so it's
        cheap to validate the whole book.
        """
        if not conids:
            return []
        try:
            data = self._ibind.security_definition_by_conid([str(c) for c in conids]).data
        except Exception as e:
            raise self._wrap(e, "secdef_by_conids") from e
        secdefs = data.get("secdef") if isinstance(data, dict) else data
        return [dict(x) for x in (secdefs or []) if isinstance(x, dict)]

    def contract_info(self, conid: int) -> dict[str, Any]:
        """`iserver/contract/{conid}/info` -> full details incl. company_name,
        currency, and `cusip` (the US-ISIN middle, so US names get an ISIN
        cross-check). One conid per call — heavier than secdef_by_conids."""
        try:
            return dict(self._ibind.contract_information_by_conid(str(conid)).data or {})
        except Exception as e:
            raise self._wrap(e, f"contract_info({conid})") from e

    def secdef_search(self, symbol: str) -> list[SecDefMatch]:
        # Skip rows with no symbol — they can't match a ticker anyway.
        return [
            SecDefMatch.model_validate(x)
            for x in self.secdef_search_raw(symbol)
            if x.get("symbol") is not None
        ]

    def resolve_conid(self, symbol: str, exchange: str, *, asset_class: str = "STK") -> int:
        matches = self.secdef_search(symbol)
        symbol_upper = symbol.upper()
        exchange_upper = exchange.upper()
        for m in matches:
            if m.symbol.upper() != symbol_upper:
                continue
            for section in m.sections:
                if str(section.get("secType", "")).upper() != asset_class.upper():
                    continue
                exch_list = str(section.get("exchange", "")).upper()
                if exchange_upper in {e.strip() for e in exch_list.split(",")}:
                    return m.conid
        for m in matches:
            if m.symbol.upper() != symbol_upper:
                continue
            for section in m.sections:
                if str(section.get("secType", "")).upper() == asset_class.upper():
                    log.warning(
                        "exchange %s not listed for %s; using conid %d anyway",
                        exchange,
                        symbol,
                        m.conid,
                    )
                    return m.conid
        raise IBKRError(f"no {asset_class} match for symbol={symbol!r} exchange={exchange!r}")

    # ----- order placement -------------------------------------------------

    def place_midprice_day_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: int,
        listing_exchange: str | None = None,
    ) -> list[PlaceOrderReply]:
        """Submit a single MIDPRICE DAY order via IBind.

        MIDPRICE pegs the order to the bid-ask midpoint and lets IBKR adjust
        as the market moves, auto-escalating up to the offer (buys) / down to
        the bid (sells) if not filled. Good default for liquid ETFs where we
        want a "smart" fill near mid rather than blind MKT slippage.

        IBind handles the reply chain internally using `_AUTO_ANSWER_ALL`, so
        the returned list always has a single element of kind="confirmed" on
        success. Errors raise IBKRError; we never return kind="error" replies
        because IBind raises ExternalBrokerError instead.
        """
        order = OrderRequest(
            conid=conid,
            side=side.value,
            quantity=float(quantity),
            order_type="MIDPRICE",
            acct_id=account_id,
            tif="DAY",
            manual_indicator=False,
            listing_exchange=listing_exchange,
        )
        try:
            result = self._ibind.place_order(order, _AUTO_ANSWER_ALL, account_id=account_id)
        except Exception as e:
            raise self._wrap(e, f"place_order({side.value} {quantity} conid={conid})") from e
        return _parse_order_reply_list(result.data)

    def what_if_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: int,
        listing_exchange: str | None = None,
    ) -> dict[str, Any]:
        """Preview commission + margin impact for a MIDPRICE DAY order; no place.

        Returns IBKR's raw whatif response (commission, init_margin,
        maint_margin, equity_with_loan, etc.). Shape varies by account.
        """
        order = OrderRequest(
            conid=conid,
            side=side.value,
            quantity=float(quantity),
            order_type="MIDPRICE",
            acct_id=account_id,
            tif="DAY",
            manual_indicator=False,
            listing_exchange=listing_exchange,
        )
        try:
            result = self._ibind.whatif_order(order, account_id=account_id)
        except Exception as e:
            raise self._wrap(e, f"whatif_order({side.value} {quantity} conid={conid})") from e
        return dict(result.data or {})

    def what_if_market_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: float,
        listing_exchange: str | None = None,
    ) -> dict[str, Any]:
        """Preview commission + margin for a MKT DAY order; no place. Unlike the
        MIDPRICE preview, `quantity` may be fractional — fractional shares on
        IBKR require a MKT/LMT order (MIDPRICE is whole-share only)."""
        order = OrderRequest(
            conid=conid,
            side=side.value,
            quantity=float(quantity),
            order_type="MKT",
            acct_id=account_id,
            tif="DAY",
            manual_indicator=False,
            listing_exchange=listing_exchange,
        )
        try:
            result = self._ibind.whatif_order(order, account_id=account_id)
        except Exception as e:
            raise self._wrap(e, f"whatif_market({side.value} {quantity} conid={conid})") from e
        return dict(result.data or {})

    def place_market_day_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: float,
        listing_exchange: str | None = None,
    ) -> list[PlaceOrderReply]:
        """Submit a single MKT DAY order (supports a fractional `quantity`).

        Used by the manual single-stock test-buy path — a small, user-confirmed
        order sized as a % of NAV. IBind walks the reply chain internally, so a
        success returns one kind="confirmed" reply; errors raise IBKRError."""
        order = OrderRequest(
            conid=conid,
            side=side.value,
            quantity=float(quantity),
            order_type="MKT",
            acct_id=account_id,
            tif="DAY",
            manual_indicator=False,
            listing_exchange=listing_exchange,
        )
        try:
            result = self._ibind.place_order(order, _AUTO_ANSWER_ALL, account_id=account_id)
        except Exception as e:
            raise self._wrap(e, f"place_market({side.value} {quantity} conid={conid})") from e
        return _parse_order_reply_list(result.data)

    def confirm_reply(self, reply_id: str, *, confirmed: bool = True) -> list[PlaceOrderReply]:
        """Rarely called in practice (IBind auto-walks the reply chain), but
        kept for back-compat with the executor's chain-walker logic.
        """
        try:
            result = self._ibind.reply(reply_id, confirmed=confirmed)
        except Exception as e:
            raise self._wrap(e, f"reply({reply_id})") from e
        return _parse_order_reply_list(result.data)

    # ----- order status ----------------------------------------------------

    def order_status(self, order_id: str) -> dict[str, Any]:
        try:
            return dict(self._ibind.order_status(order_id).data or {})
        except Exception as e:
            raise self._wrap(e, f"order_status({order_id})") from e

    def live_orders(self) -> list[dict[str, Any]]:
        try:
            data = self._ibind.live_orders().data or {}
            return list(data.get("orders", []))
        except Exception as e:
            raise self._wrap(e, "live_orders") from e

    # ----- portfolio summary / market data ---------------------------------

    def portfolio_summary(self, account_id: str) -> dict[str, Any]:
        try:
            return dict(self._ibind.portfolio_summary(account_id=account_id).data or {})
        except Exception as e:
            raise self._wrap(e, "portfolio_summary") from e

    def init_brokerage_session(self) -> None:
        """Initialize the iserver brokerage session — required before
        /iserver/marketdata/snapshot, which otherwise 500s with
        'Please query /accounts first'. Idempotent; safe to call once up front."""
        try:
            self._ibind.receive_brokerage_accounts()
        except Exception as e:
            raise self._wrap(e, "init_brokerage_session") from e

    def marketdata_snapshot(
        self, conids: list[int], *, fields: list[str] | None = None, warmups: int = 1
    ) -> list[dict[str, Any]]:
        """Live market-data snapshot. IBKR primes the feed on first request and
        returns the requested fields only on a follow-up call, so `warmups`
        repeats the call (discarding early partial rows) before returning."""
        if not conids:
            return []
        try:
            data: Any = []
            for _ in range(max(1, warmups + 1)):
                data = (
                    self._ibind.live_marketdata_snapshot(
                        conids=[str(c) for c in conids],
                        fields=fields or ["31"],
                    ).data
                    or []
                )
                if warmups:
                    time.sleep(0.6)
            return list(data)
        except Exception as e:
            raise self._wrap(e, "marketdata_snapshot") from e

    # ----- internals -------------------------------------------------------

    def _wrap(self, e: BaseException, context: str) -> IBKRError:
        if isinstance(e, ExternalBrokerError):
            msg = str(e)
            if "401" in msg or "403" in msg or "Unauthorized" in msg or "Forbidden" in msg:
                return IBKRAuthError(f"OAuth unauthorized during {context}: {e}")
        return IBKRError(f"IBKR error during {context}: {e}")


# ----- helpers (unchanged from pre-OAuth shape) ----------------------------


def _to_current_position(raw: dict[str, Any]) -> CurrentPosition:
    mkt_price = _to_decimal(raw["mktPrice"]) if raw.get("mktPrice") is not None else None
    return CurrentPosition(
        conid=int(raw["conid"]),
        symbol=str(raw.get("contractDesc") or raw.get("ticker") or raw["conid"]),
        asset_class=str(raw.get("assetClass", "STK")),
        quantity=_to_decimal(raw["position"]),
        market_value=_to_decimal(raw.get("mktValue", 0)),
        currency=str(raw.get("currency", "USD")),
        mkt_price=mkt_price,
    )


def _to_decimal(v: Any) -> Decimal:
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def _parse_order_reply_list(data: Any) -> list[PlaceOrderReply]:
    if data is None:
        return []
    if isinstance(data, dict):
        return [PlaceOrderReply.model_validate(data)]
    if isinstance(data, list):
        return [PlaceOrderReply.model_validate(x) for x in data]
    raise IBKRError(f"unexpected order reply shape: {type(data).__name__}")
