"""eToro brokerage client — implements the broker-agnostic `Broker` Protocol.

Talks to eToro's public REST API (https://public-api.etoro.com). Auth is three
headers on EVERY request: `x-api-key` (the app/public key), `x-user-key` (a
per-environment user key), and `x-request-id` (a unique UUID). Keys are
environment-scoped: a key works for DEMO or REAL, never both — pick with
`ETORO_ENV`. Demo simply inserts a `demo/` segment into the execution/info paths.

Deliberately independent of `ibkr_client`: no ibind, no conids, no shared HTTP
session. Buy = open a long at market; sell = close an existing long by units
(needs the eToro positionId, which the caller tracks). Docs / key management:
https://api-portal.etoro.com/

Endpoints used (real → demo):
  GET  /api/v1/market-data/search?internalSymbolFull=SYM   (symbol → instrumentId)
  POST /api/v2/trading/info/costs        → /api/v2/trading/info/demo/costs
  POST /api/v2/trading/execution/orders  → /api/v2/trading/execution/demo/orders
  POST /api/v1/trading/execution/market-close-orders/positions/{id}
                                         → .../execution/demo/market-close-orders/...
  GET  /api/v1/trading/info/pnl          → /api/v1/trading/info/demo/pnl  (balance)
"""

from __future__ import annotations

import contextlib
import uuid
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from etoro_yfinance.broker import (
    Balance,
    BrokerAuthError,
    BrokerError,
    Candle,
    CostLine,
    Instrument,
    OrderPreview,
    OrderResult,
)

# eToro candle intervals accepted by the history endpoint.
CANDLE_INTERVALS = (
    "OneMinute",
    "FiveMinutes",
    "TenMinutes",
    "FifteenMinutes",
    "ThirtyMinutes",
    "OneHour",
    "FourHours",
    "OneDay",
    "OneWeek",
)
_MAX_CANDLES = 1000  # hard cap per request (no date-range param exists)

BASE_URL = "https://public-api.etoro.com"
ETORO_DEMO = "demo"
ETORO_REAL = "real"

# eToro real-stock settlement (own the shares, 1x). What-if requires a settlement
# type; "real" is the cash-equity, non-CFD choice that matches a long-only book.
_SETTLEMENT_TYPE = "real"


def _to_decimal(v: Any) -> Decimal | None:
    if v is None:
        return None
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None


def _find_candle_list(obj: Any) -> list[dict[str, Any]] | None:
    """The candle endpoint nests the OHLCV array inside an envelope (grouped by
    instrument, alongside range aggregates) whose exact shape isn't documented.
    Depth-first find the first list of candle dicts (items with open+close)."""
    if isinstance(obj, list):
        if obj and isinstance(obj[0], dict) and "open" in obj[0] and "close" in obj[0]:
            return obj
        for it in obj:
            found = _find_candle_list(it)
            if found is not None:
                return found
    elif isinstance(obj, dict):
        for v in obj.values():
            found = _find_candle_list(v)
            if found is not None:
                return found
    return None


def _err_body(r: httpx.Response) -> str:
    try:
        return str(r.json())[:400]
    except ValueError:
        return r.text[:400]


class EtoroClient:
    """A `broker.Broker` implementation for eToro. Use as a context manager so
    the underlying HTTP connection pool is closed."""

    name = "etoro"

    def __init__(
        self,
        *,
        api_key: str,
        user_key: str,
        env: str = ETORO_DEMO,
        order_currency: str = "usd",
        default_leverage: int = 1,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key or not user_key:
            raise BrokerAuthError(
                "eToro API key and user key are required "
                "(set ETORO_API_KEY / ETORO_USER_KEY in .env)"
            )
        if env not in (ETORO_DEMO, ETORO_REAL):
            raise BrokerError(f"ETORO_ENV must be 'demo' or 'real', got {env!r}")
        self._env = env
        self._order_currency = order_currency
        self._default_leverage = default_leverage
        self._client = httpx.Client(
            base_url=BASE_URL,
            timeout=timeout,
            transport=transport,
            headers={
                "x-api-key": api_key,
                "x-user-key": user_key,
                "Content-Type": "application/json",
            },
        )

    # ── lifecycle ────────────────────────────────────────────────────────────
    def __enter__(self) -> EtoroClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        with contextlib.suppress(Exception):  # best-effort; never mask the original error
            self._client.close()

    @property
    def is_demo(self) -> bool:
        return self._env == ETORO_DEMO

    @property
    def _seg(self) -> str:
        """The path segment that switches an execution/info endpoint to demo."""
        return "demo/" if self.is_demo else ""

    # ── low-level request ────────────────────────────────────────────────────
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {"x-request-id": str(uuid.uuid4())}  # unique per request, for tracing
        try:
            r = self._client.request(method, path, params=params, json=json, headers=headers)
        except httpx.HTTPError as e:
            raise BrokerError(f"eToro request failed ({method} {path}): {e}") from e
        if r.status_code in (401, 403):
            raise BrokerAuthError(
                f"eToro auth rejected ({r.status_code}) on {method} {path}: {_err_body(r)}"
            )
        if r.status_code >= 400:
            raise BrokerError(f"eToro API error {r.status_code} on {method} {path}: {_err_body(r)}")
        if not r.content:
            return {}
        try:
            data = r.json()
        except ValueError as e:
            raise BrokerError(f"eToro returned non-JSON on {method} {path}: {r.text[:200]}") from e
        return data if isinstance(data, dict) else {"items": data}

    # ── Broker protocol ──────────────────────────────────────────────────────
    def resolve_symbol(self, symbol: str) -> Instrument:
        """Resolve a ticker to an eToro instrument. The search may return partial
        matches, so we require an EXACT `internalSymbolFull` hit (per eToro's
        docs) rather than trusting the first row."""
        data = self._request(
            "GET", "/api/v1/market-data/search", params={"internalSymbolFull": symbol}
        )
        items = data.get("items") or []
        want = symbol.strip().upper()
        for it in items:
            if str(it.get("internalSymbolFull", "")).upper() == want:
                return self._instrument(it, symbol)
        if items:
            seen = [i.get("internalSymbolFull") for i in items][:5]
            raise BrokerError(f"eToro: no exact instrument for {symbol!r} (search returned {seen})")
        raise BrokerError(f"eToro: no instrument found for {symbol!r}")

    def preview_buy(
        self,
        *,
        instrument: Instrument,
        amount: Decimal | None = None,
        units: Decimal | None = None,
        leverage: int | None = None,
    ) -> OrderPreview:
        """What-if cost breakdown for opening a long — no order is placed."""
        body = self._open_body(instrument, amount, units, leverage)
        body["settlementType"] = _SETTLEMENT_TYPE  # required for a what-if open
        data = self._request("POST", f"/api/v2/trading/info/{self._seg}costs", json=body)
        return self._preview(data, instrument)

    def buy(
        self,
        *,
        instrument: Instrument,
        amount: Decimal | None = None,
        units: Decimal | None = None,
        leverage: int | None = None,
    ) -> OrderResult:
        """Open a long at market, by notional `amount` or by `units` (exactly
        one). Returns the eToro orderId. Placement is real money in REAL env."""
        body = self._open_body(instrument, amount, units, leverage)
        data = self._request("POST", f"/api/v2/trading/execution/{self._seg}orders", json=body)
        oid = data.get("orderId")
        return OrderResult(
            broker=self.name,
            order_id=str(oid) if oid is not None else "",
            status="submitted",
            raw=data,
        )

    def close_position(
        self, *, position_id: str, instrument_id: str, units: Decimal | None = None
    ) -> OrderResult:
        """Sell = close an existing long. Closes `units` of the position, or the
        whole position when `units` is None. Needs both the eToro positionId and
        its instrumentId (the caller tracks these from the open)."""
        body: dict[str, Any] = {"InstrumentId": int(instrument_id)}
        if units is not None:
            body["UnitsToDeduct"] = float(units)
        path = f"/api/v1/trading/execution/{self._seg}market-close-orders/positions/{position_id}"
        data = self._request("POST", path, json=body)
        ofc = data.get("orderForClose") or {}
        oid = ofc.get("orderID") or ofc.get("orderId")
        return OrderResult(
            broker=self.name,
            order_id=str(oid) if oid is not None else "",
            status="closing",
            raw=data,
        )

    def candles(
        self,
        instrument_id: str,
        *,
        interval: str = "OneDay",
        count: int = _MAX_CANDLES,
        direction: str = "desc",
    ) -> list[Candle]:
        """OHLCV history for one instrument. `interval` is an eToro granularity
        (e.g. 'OneDay'); `count` is capped at 1000 (the endpoint has no date-range
        param, so you get the most recent `count` bars). Returned oldest-first
        regardless of `direction`."""
        if interval not in CANDLE_INTERVALS:
            raise BrokerError(f"interval must be one of {CANDLE_INTERVALS}, got {interval!r}")
        n = max(1, min(int(count), _MAX_CANDLES))
        path = (
            f"/api/v1/market-data/instruments/{instrument_id}"
            f"/history/candles/{direction}/{interval}/{n}"
        )
        data = self._request("GET", path)
        rows = _find_candle_list(data) or []
        candles = [
            Candle(
                date=str(r.get("fromDate") or ""),
                open=_to_decimal(r.get("open")),
                high=_to_decimal(r.get("high")),
                low=_to_decimal(r.get("low")),
                close=_to_decimal(r.get("close")),
                volume=_to_decimal(r.get("volume")),
            )
            for r in rows
        ]
        candles.sort(key=lambda c: c.date)  # normalise to oldest-first
        return candles

    def instrument_types(self) -> list[dict[str, Any]]:
        """eToro's asset-type catalog: [{id, name}] (Stocks, ETF, Crypto, ...)."""
        data = self._request("GET", "/api/v1/market-data/instrument-types")
        return [
            {"id": t.get("instrumentTypeID"), "name": t.get("instrumentTypeDescription")}
            for t in data.get("instrumentTypes", [])
        ]

    def exchanges(self) -> list[dict[str, Any]]:
        """eToro's exchange catalog: [{id, name}] (Nasdaq, NYSE, LSE, TYO, ...)."""
        data = self._request("GET", "/api/v1/market-data/exchanges")
        return [
            {"id": e.get("exchangeID"), "name": e.get("exchangeDescription")}
            for e in data.get("exchangeInfo", [])
        ]

    def list_instruments(self, *, type_ids: list[int] | None = None) -> list[dict[str, Any]]:
        """The whole tradable universe (or just the given types), one call per
        type via display-data-by-type. eToro has no Asset-Explorer/discover access
        on this key, but `market-data/instruments?instrumentTypeIds=N` returns
        every instrument of a type. Each row: instrument_id, symbol, type_id,
        exchange_id, name (no ISIN — eToro doesn't publish it)."""
        if type_ids is None:
            type_ids = [t["id"] for t in self.instrument_types() if t["id"] is not None]
        out: list[dict[str, Any]] = []
        for tid in type_ids:
            data = self._request(
                "GET", "/api/v1/market-data/instruments", params={"instrumentTypeIds": tid}
            )
            for r in data.get("instrumentDisplayDatas", []):
                out.append(
                    {
                        "instrument_id": r.get("instrumentID"),
                        "symbol": r.get("symbolFull"),
                        "type_id": r.get("instrumentTypeID"),
                        "exchange_id": r.get("exchangeID"),
                        "name": r.get("instrumentDisplayName"),
                        "is_internal": bool(r.get("isInternalInstrument")),
                        "stocks_industry_id": r.get("stocksIndustryID"),
                    }
                )
        return out

    def stocks_industries(self) -> dict[int, str]:
        """eToro's stock sector taxonomy: {industryID: name} (9 legacy buckets —
        Technology, Financial, Healthcare, …). Resolves the stocksIndustryID that
        rides along on each stock in list_instruments()."""
        data = self._request("GET", "/api/v1/market-data/stocks-industries")
        return {
            i.get("industryID"): i.get("industryName")
            for i in data.get("stocksIndustries", [])
            if i.get("industryID") is not None
        }

    def eligibility(
        self,
        instrument_ids: list[int],
        *,
        currency: str = "USD",
    ) -> dict[int, dict[str, Any]]:
        """Per-instrument trading rules for the authenticated (env-aware) account
        — position limits, permitted order types, SL/TP bounds and available
        leverage. Places NO orders. Batches of <=100 (API cap). Returns
        {instrument_id: eligibility-dict} for instruments the API recognised."""
        out: dict[int, dict[str, Any]] = {}
        ids = [int(i) for i in instrument_ids]
        for i in range(0, len(ids), 100):
            data = self._request(
                "POST",
                f"/api/v2/trading/info/{self._seg}eligibility",
                json={"instrumentIds": ids[i : i + 100], "currency": currency},
            )
            for e in data.get("eligibilities", []):
                iid = e.get("instrumentId")
                if iid is not None:
                    out[int(iid)] = e
        return out

    def market_rates(self, instrument_ids: list[int]) -> dict[int, dict[str, Any]]:
        """Live bid/ask (+ margins) per instrument — the spread is a direct
        liquidity/cost signal. Batches of <=100. The API wants a raw
        comma-separated list (httpx would percent-encode a `params` comma → 500),
        so we build the query inline. Returns {instrument_id: rate-dict}."""
        out: dict[int, dict[str, Any]] = {}
        ids = [int(i) for i in instrument_ids]
        for i in range(0, len(ids), 100):
            q = ",".join(str(x) for x in ids[i : i + 100])
            data = self._request("GET", f"/api/v1/market-data/instruments/rates?instrumentIds={q}")
            for r in data.get("rates", []):
                iid = r.get("instrumentID")
                if iid is not None:
                    out[int(iid)] = r
        return out

    def balance(self) -> Balance:
        """Account value from the env-aware portfolio/PnL endpoint. We deliberately
        do NOT use eToro's aggregated `/api/v1/balances`: it requires a distinct
        `etoro-public:money.balance:read` scope (not granted to demo tokens under
        the basic Read permission) and has no demo variant. `trading/info/{demo/}
        pnl` works with basic Read and reflects the selected environment.

        `cash` = credit (available trading balance, USD). `total` mirrors it —
        eToro doesn't return a single equity figure here; open-position detail
        lives in `raw['clientPortfolio']['positions']`."""
        data = self._request("GET", f"/api/v1/trading/info/{self._seg}pnl")
        cp = data.get("clientPortfolio") or {}
        credit = _to_decimal(cp.get("credit"))
        return Balance(total=credit, cash=credit, currency="USD", raw=data)

    # ── helpers ──────────────────────────────────────────────────────────────
    def _instrument(self, it: dict[str, Any], symbol: str) -> Instrument:
        iid = it.get("instrumentId")
        if iid is None:
            raise BrokerError(f"eToro search item for {symbol!r} has no instrumentId")
        return Instrument(
            broker=self.name,
            instrument_id=str(iid),
            symbol=str(it.get("internalSymbolFull") or symbol),
            name=str(it.get("instrumentDisplayName") or ""),
            currency=str(it.get("instrumentCurrency") or ""),
        )

    def _open_body(
        self,
        instrument: Instrument,
        amount: Decimal | None,
        units: Decimal | None,
        leverage: int | None,
    ) -> dict[str, Any]:
        if (amount is None) == (units is None):
            raise BrokerError("specify exactly one of amount or units")
        body: dict[str, Any] = {
            "action": "open",
            "transaction": "buy",
            "instrumentId": int(instrument.instrument_id),
            "orderType": "mkt",
            "leverage": int(leverage or self._default_leverage),
        }
        if amount is not None:
            body["amount"] = float(amount)
            body["orderCurrency"] = self._order_currency
        else:
            assert units is not None  # guaranteed by the exactly-one check above
            body["units"] = float(units)
        return body

    def _preview(self, data: dict[str, Any], instrument: Instrument) -> OrderPreview:
        lines: list[CostLine] = []
        total = Decimal("0")
        ccy = ""
        for c in data.get("costs") or []:
            amt = _to_decimal(c.get("amount"))
            cur = str(c.get("currency") or "")
            if amt is not None:
                total += amt
            if cur:
                ccy = cur
            lines.append(
                CostLine(
                    kind=str(c.get("costType") or ""), amount=amt or Decimal("0"), currency=cur
                )
            )
        return OrderPreview(
            instrument_id=str(data.get("instrumentId") or instrument.instrument_id),
            symbol=str(data.get("symbol") or instrument.symbol),
            est_cost=total if lines else None,
            currency=ccy or instrument.currency,
            lines=lines,
            raw=data,
        )


def _select_user_key(settings: Any) -> str:
    """Pick the user key matching ETORO_ENV: the real key for 'real', the demo
    key for 'demo', falling back to the generic `etoro_user_key` if the
    env-specific one is unset."""
    specific = (
        settings.etoro_user_key_real
        if settings.etoro_env == ETORO_REAL
        else settings.etoro_user_key_demo
    )
    key = specific or settings.etoro_user_key
    return key.get_secret_value() if key else ""


def etoro_from_settings(
    settings: Any, *, transport: httpx.BaseTransport | None = None
) -> EtoroClient:
    """Build an `EtoroClient` from the app `Settings` (config.py). Selects the
    demo vs real user key by ETORO_ENV. Raises `BrokerAuthError` if the selected
    env's key (or the public key) isn't configured."""
    api_key = settings.etoro_api_key.get_secret_value() if settings.etoro_api_key else ""
    return EtoroClient(
        api_key=api_key,
        user_key=_select_user_key(settings),
        env=settings.etoro_env,
        order_currency=settings.etoro_order_currency,
        default_leverage=settings.etoro_default_leverage,
        timeout=settings.http_timeout_seconds,
        transport=transport,
    )
