"""Thin synchronous httpx wrapper around the IBKR Client Portal API (cpapi-v1).

All requests are sent to a locally-hosted IBeam gateway, default
`https://localhost:5000/v1/api`. The gateway uses a self-signed cert; TLS
verification is off by default for that reason.

Endpoint coverage is limited to what the rebalancer needs:
  - auth: /iserver/auth/status, /iserver/reauthenticate, /tickle
  - account discovery: /iserver/accounts, /portfolio/accounts
  - positions: /portfolio/{accountId}/positions/{pageId}
  - symbol resolution: /iserver/secdef/search
  - orders: /iserver/account/{accountId}/orders, /iserver/reply/{replyId},
            /iserver/account/orders, /iserver/account/order/status/{orderId}
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from decimal import Decimal
from types import TracebackType
from typing import Any, Self

import httpx
from pydantic import BaseModel, ConfigDict

from .schema import CurrentPosition, OrderSide

log = logging.getLogger(__name__)

# IBKR returns at most 100 positions per page; treat anything < 100 as last page.
POSITIONS_PAGE_SIZE = 100


class IBKRError(Exception):
    """Raised when the gateway returns a non-2xx response or an embedded error."""


class IBKRAuthError(IBKRError):
    """Raised when the gateway reports the session as unauthenticated."""


class AuthStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    authenticated: bool = False
    connected: bool = False
    competing: bool = False
    message: str = ""


class SecDefMatch(BaseModel):
    """A single match from /iserver/secdef/search.

    The `sections` list contains per-exchange variants; we use it to verify
    that the desired listing exchange is available for the returned conid.
    """

    model_config = ConfigDict(extra="ignore")

    conid: int
    symbol: str
    description: str | None = None
    sections: list[dict[str, Any]] = []


class PlaceOrderReply(BaseModel):
    """One element of the response from `place_order` or `confirm_reply`.

    Three distinct shapes share the wire format:
      - confirmed:      {order_id, order_status, encrypt_message}
      - reply required: {id, message: [...], isSuppressed, messageIds: [...]}
      - rejected:       {error: "..."} (still 200 OK)

    Pydantic accepts all fields as optional and the caller branches on which
    are present via `kind`.
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


class IBKRClient:
    """Synchronous client for the local IBKR Client Portal gateway.

    Use as a context manager; the underlying httpx.Client is closed on exit.
    """

    def __init__(
        self,
        gateway_url: str,
        *,
        verify_ssl: bool = False,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        base = gateway_url.rstrip("/")
        if not base.endswith("/v1/api"):
            base = f"{base}/v1/api"
        self._base = base
        self._client = httpx.Client(
            base_url=self._base,
            verify=verify_ssl,
            timeout=timeout,
            transport=transport,
            headers={"User-Agent": "ibkr-portfolio-connect/0.1"},
        )

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
        self._client.close()

    # ----- low-level -------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            resp = self._client.request(method, path, **kwargs)
        except httpx.HTTPError as e:
            raise IBKRError(f"network error contacting gateway: {e}") from e
        if resp.status_code == 401:
            raise IBKRAuthError(f"gateway returned 401 for {method} {path}")
        if resp.status_code >= 400:
            raise IBKRError(
                f"gateway returned {resp.status_code} for {method} {path}: {resp.text[:500]}"
            )
        if not resp.content:
            return None
        return resp.json()

    # ----- auth / session --------------------------------------------------

    def auth_status(self) -> AuthStatus:
        data = self._request("POST", "/iserver/auth/status")
        return AuthStatus.model_validate(data)

    def reauthenticate(self) -> None:
        self._request("POST", "/iserver/reauthenticate")

    def tickle(self) -> dict[str, Any]:
        return self._request("POST", "/tickle") or {}

    def ensure_authenticated(self) -> AuthStatus:
        """Return the current auth status; raise IBKRAuthError if not connected.

        Triggers a single `reauthenticate` retry on a non-authenticated session
        before giving up. Does not loop indefinitely.
        """
        status = self.auth_status()
        if status.authenticated and status.connected:
            return status
        log.info("session not authenticated; attempting reauthenticate")
        self.reauthenticate()
        status = self.auth_status()
        if not (status.authenticated and status.connected):
            raise IBKRAuthError(
                f"session not authenticated after reauthenticate: {status.message!r}"
            )
        return status

    # ----- accounts --------------------------------------------------------

    def iserver_accounts(self) -> list[str]:
        """Return account IDs visible to the iserver session (side effect: sets context)."""
        data = self._request("GET", "/iserver/accounts") or {}
        accounts = data.get("accounts", [])
        return [str(a) for a in accounts]

    def portfolio_accounts(self) -> list[dict[str, Any]]:
        """Return full portfolio account metadata. Must be called before /portfolio/{id}/positions."""
        data = self._request("GET", "/portfolio/accounts") or []
        return list(data)

    # ----- positions -------------------------------------------------------

    def positions(self, account_id: str) -> list[CurrentPosition]:
        """Return every position in the account, paged to exhaustion."""
        all_raw: list[dict[str, Any]] = []
        for page in self._iter_pages(account_id):
            all_raw.extend(page)
        return [_to_current_position(item) for item in all_raw]

    def _iter_pages(self, account_id: str) -> Iterator[list[dict[str, Any]]]:
        page = 0
        while True:
            data = self._request("GET", f"/portfolio/{account_id}/positions/{page}") or []
            yield list(data)
            if len(data) < POSITIONS_PAGE_SIZE:
                return
            page += 1

    # ----- symbol resolution ----------------------------------------------

    def secdef_search(self, symbol: str) -> list[SecDefMatch]:
        data = self._request("GET", "/iserver/secdef/search", params={"symbol": symbol}) or []
        return [SecDefMatch.model_validate(x) for x in data]

    def resolve_conid(self, symbol: str, exchange: str, *, asset_class: str = "STK") -> int:
        """Look up the IBKR conid for a given (symbol, exchange) pair.

        Picks the first match where (a) the symbol equals `symbol`, and (b) one
        of the per-exchange `sections` lists `asset_class` and (best-effort)
        mentions `exchange`. Raises `IBKRError` if no plausible match is found.
        """
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
                # IBKR's `exchange` field can be a comma-separated list, e.g.
                # "ARCA,BATS,NYSE" — accept membership.
                if exchange_upper in {e.strip() for e in exch_list.split(",")}:
                    return m.conid
        # Fall back: a single perfect symbol match with the desired secType,
        # exchange unmatched. Better than failing entirely for tickers with
        # idiosyncratic exchange names.
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

    def place_market_day_order(
        self,
        account_id: str,
        *,
        conid: int,
        side: OrderSide,
        quantity: int,
        listing_exchange: str | None = None,
    ) -> list[PlaceOrderReply]:
        """Submit a single MKT DAY order. Returns the raw reply list from IBKR."""
        order: dict[str, Any] = {
            "acctId": account_id,
            "conid": conid,
            "orderType": "MKT",
            "side": side.value,
            "tif": "DAY",
            "quantity": quantity,
            # We're an automated tool, not a manual UI entry.
            "manualIndicator": False,
        }
        if listing_exchange is not None:
            order["listingExchange"] = listing_exchange
        data = self._request(
            "POST",
            f"/iserver/account/{account_id}/orders",
            json={"orders": [order]},
        )
        return _parse_order_reply_list(data)

    def confirm_reply(self, reply_id: str, *, confirmed: bool = True) -> list[PlaceOrderReply]:
        data = self._request("POST", f"/iserver/reply/{reply_id}", json={"confirmed": confirmed})
        return _parse_order_reply_list(data)

    # ----- order status ----------------------------------------------------

    def order_status(self, order_id: str) -> dict[str, Any]:
        data = self._request("GET", f"/iserver/account/order/status/{order_id}") or {}
        return dict(data)

    def live_orders(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/iserver/account/orders") or {}
        return list(data.get("orders", []))

    # ----- portfolio summary / market data ---------------------------------

    def portfolio_summary(self, account_id: str) -> dict[str, Any]:
        """Account summary including netliquidation, totalcashvalue, etc."""
        data = self._request("GET", f"/portfolio/{account_id}/summary") or {}
        return dict(data)

    def marketdata_snapshot(
        self, conids: list[int], *, fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Return /iserver/marketdata/snapshot rows for each conid.

        Note: IBKR's first call sometimes returns empty data (the gateway has
        to "warm up"); callers should retry once after a short delay. We do
        not retry here so testing stays deterministic.
        """
        if not conids:
            return []
        params = {
            "conids": ",".join(str(c) for c in conids),
            "fields": ",".join(fields or ["31"]),  # 31 = Last Price
        }
        data = self._request("GET", "/iserver/marketdata/snapshot", params=params) or []
        return list(data)


# ----- helpers -------------------------------------------------------------


def _to_current_position(raw: dict[str, Any]) -> CurrentPosition:
    """Normalize one item from /portfolio/{id}/positions/{page} into our type.

    `mktValue` can be negative for short positions; we preserve the sign in
    `quantity` and store `market_value` as the signed economic value too.
    """
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
    """Convert a JSON number to Decimal without going through float."""
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def _parse_order_reply_list(data: Any) -> list[PlaceOrderReply]:
    """Parse the IBKR place-order response, which is sometimes a list and
    sometimes a single object (in the 200-with-error case)."""
    if data is None:
        return []
    if isinstance(data, dict):
        return [PlaceOrderReply.model_validate(data)]
    if isinstance(data, list):
        return [PlaceOrderReply.model_validate(x) for x in data]
    raise IBKRError(f"unexpected order reply shape: {type(data).__name__}")
