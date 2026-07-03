> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Search for Instruments

> **Rate limit:** 120 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `GET /api/v1/market-data/exchanges`
- `GET /api/v1/market-data/instrument-types`
- `GET /api/v1/market-data/instruments`
- `GET /api/v1/market-data/instruments/history/closing-price`
- `GET /api/v1/market-data/instruments/rates`
- `GET /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}`
- `GET /api/v1/market-data/stocks-industries`

---

Retrieve a paginated list of instruments. Any field in the Instrument response schema can be projected via the required `fields` parameter and/or used as a query-string filter (e.g. `fields=instrumentId,displayname&displayname=Bitcoin`). Use `pageSize`/`pageNumber` to paginate and `sort` to order. Filters that do not match an indexed instrument field are ignored.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/market-data/search
openapi: 3.0.1
info:
  title: eToro Api
  version: v1.279.0
  description: >-
    eToro’s public API provides access to real-time financial data, trading
    insights, and account management features, allowing developers to integrate
    eToro’s services into their applications. With access to market prices,
    historical data, and social trading information, the API empowers users to
    enhance their trading strategies. Designed for security and scalability, the
    eToro API ensures smooth and reliable integration for a variety of financial
    applications.


    For more details on integrating with eToro's public WebSocket service,
    please refer to the dedicated [WebSocket
    documentation](./websocket/websocket-doc.html).
servers:
  - url: https://public-api.etoro.com
    description: eToro Public API
security: []
tags:
  - name: Agent Portfolios
  - name: Social Feeds
  - name: Balances
  - name: Clubs
  - name: Watchlists
  - name: Asset Explorer
  - name: Market Data
  - name: Identity
  - name: Cash Accounts
  - name: Notifications
  - name: PI Data
  - name: Price Alerts
  - name: Sub Accounts eToro Trading
  - name: Sub Accounts
  - name: Trading Demo
  - name: Trading Real
  - name: Users Info
  - name: User Stats
  - name: Deprecated
paths:
  /api/v1/market-data/search:
    get:
      tags:
        - Market Data
      summary: Search for Instruments
      description: >-
        **Rate limit:** 120 requests per 60 seconds. This is a **shared quota**
        — the same budget is consumed by a group of related endpoints, so
        calling any of them reduces what is left for the others (you cannot call
        each at the full rate independently). Endpoints sharing this quota:

        - `GET /api/v1/market-data/exchanges`

        - `GET /api/v1/market-data/instrument-types`

        - `GET /api/v1/market-data/instruments`

        - `GET /api/v1/market-data/instruments/history/closing-price`

        - `GET /api/v1/market-data/instruments/rates`

        - `GET
        /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}`

        - `GET /api/v1/market-data/stocks-industries`


        ---


        Retrieve a paginated list of instruments. Any field in the Instrument
        response schema can be projected via the required `fields` parameter
        and/or used as a query-string filter (e.g.
        `fields=instrumentId,displayname&displayname=Bitcoin`). Use
        `pageSize`/`pageNumber` to paginate and `sort` to order. Filters that do
        not match an indexed instrument field are ignored.
      operationId: getMarketDataSearch
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: fe61fc5f-42e9-4c32-9b2a-43b36fa47743
          description: A unique request identifier.
        - name: x-api-key
          in: header
          required: true
          schema:
            type: string
            format: password
            example: lhgfaslk21490FAScVPkdsb53F9dNkfHG4faZSG5vfjndfcfgdssdgsdHF4663
          description: API key for authentication.
        - name: x-user-key
          in: header
          required: true
          schema:
            type: string
            format: password
            example: >-
              eyJlYW4iOiJVbnJlZ2lzdGVyZWRBcHBsaWNhdGlvbiIsImVrIjoiOE5sZ2cwcW5EUVdROUFNWGpXT2lmOWktZnpidG5KcUlqWGJ3WHJZZkpZcldrbG90ZEhvLVBjSWhQaU8xU1ZtMW84aU1WZGZqN2xWNzFjLXFxLmcybXE1dnh4Q1hUT25xaWRUaTFlcEhmVk1fIn0_
          description: User-specific authentication key.
        - name: pageSize
          in: query
          description: The number of results to return per page.
          required: false
          schema:
            type: integer
        - name: pageNumber
          in: query
          description: The page number to retrieve for pagination.
          required: false
          schema:
            type: integer
        - name: fields
          in: query
          description: >-
            A comma-separated list of fields to include in the response.
            Example: pop=popularityUniques7Day,displayname
          required: true
          schema:
            type: string
        - name: sort
          in: query
          description: >-
            The field to sort by, with direction (asc/desc). Example:
            popularityUniques7Day desc
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Successful response containing the list of instruments.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InstrumentInfo_InstrumentSearchResponse'
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 8 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
              schema:
                type: integer
              example: 120
            RateLimit-Remaining:
              description: Requests remaining in the current window for this quota.
              schema:
                type: integer
            RateLimit-Reset:
              description: Seconds until the current window resets.
              schema:
                type: integer
            RateLimit-Policy:
              description: Quota policy in the form `<limit>;w=<window-seconds>`.
              schema:
                type: string
              example: 120;w=60
        '429':
          description: >-
            Too Many Requests — the shared rate limit (120 requests / 60s) was
            exceeded.
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 8 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
              schema:
                type: integer
              example: 120
            RateLimit-Remaining:
              description: Requests remaining in the current window for this quota.
              schema:
                type: integer
            RateLimit-Reset:
              description: Seconds until the current window resets.
              schema:
                type: integer
            RateLimit-Policy:
              description: Quota policy in the form `<limit>;w=<window-seconds>`.
              schema:
                type: string
              example: 120;w=60
            Retry-After:
              description: Seconds to wait before retrying.
              schema:
                type: integer
              example: 60
      security:
        - oauth2:
            - etoro-public:real:read
        - oauth2:
            - etoro-public:demo:read
        - oauth2:
            - etoro-public:real:write
        - oauth2:
            - etoro-public:demo:write
        - oauth2:
            - etoro-public:market-data:read
components:
  schemas:
    InstrumentInfo_InstrumentSearchResponse:
      type: object
      properties:
        page:
          type: integer
          description: The current page number.
        pageSize:
          type: integer
          description: The number of items per page.
        totalItems:
          type: integer
          description: The total number of instruments matching the search criteria.
        items:
          type: array
          items:
            $ref: '#/components/schemas/InstrumentInfo_Instrument'
    InstrumentInfo_Instrument:
      type: object
      properties:
        instrumentId:
          type: integer
          description: A unique identifier for the instrument.
        displayname:
          type: string
          description: The display name of the instrument.
        popularityUniques7Day:
          type: integer
          description: >-
            The number of unique users who viewed this instrument in the last 7
            days.
        instrumentTypeID:
          type: integer
          description: The type ID of the instrument.
        instrumentType:
          type: string
          description: The type of the instrument.
        exchangeID:
          type: integer
          description: The ID of the exchange where the instrument is traded.
        isOpen:
          type: boolean
          description: Indicates whether the instrument is currently open for trading.
        internalAssetClassId:
          type: integer
          description: The internal asset class ID.
        internalInstrumentDisplayName:
          type: string
          description: The internal display name of the instrument.
        isInternalInstrument:
          type: boolean
          description: Indicates whether the instrument is internal.
        internalSymbolFull:
          type: string
          description: The full internal symbol of the instrument.
        isHiddenFromClient:
          type: boolean
          description: Indicates whether the instrument is hidden from clients.
        internalInstrumentId:
          type: integer
          description: The internal instrument ID.
        internalCryptoTypeId:
          type: integer
          description: The internal crypto type ID.
        internalExchangeId:
          type: integer
          description: The internal exchange ID.
        internalExchangeName:
          type: string
          description: The internal exchange name.
        internalAssetClassName:
          type: string
          description: The internal asset class name.
        logo35x35:
          type: string
          description: The URL of the 35x35 logo.
        logo50x50:
          type: string
          description: The URL of the 50x50 logo.
        logo150x150:
          type: string
          description: The URL of the 150x150 logo.
        dailyPriceChange:
          type: number
          description: The daily price change.
        absDailyPriceChange:
          type: number
          description: The absolute daily price change.
        weeklyPriceChange:
          type: number
          description: The weekly price change.
        monthlyPriceChange:
          type: number
          description: The monthly price change.
        isDelisted:
          type: boolean
          description: Indicates whether the instrument is delisted.
        isCurrentlyTradable:
          type: boolean
          description: Indicates whether the instrument is currently tradable.
        isExchangeOpen:
          type: boolean
          description: Indicates whether the exchange is open.
        internalClosingPrice:
          type: number
          description: The internal closing price.
        isActiveInPlatform:
          type: boolean
          description: Indicates whether the instrument is active in the platform.
        isBuyEnabled:
          type: boolean
          description: Indicates whether buying is enabled for the instrument.
        currentRate:
          type: number
          description: The current rate of the instrument.
        threeMonthPriceChange:
          type: number
          description: The three-month price change.
        sixMonthPriceChange:
          type: number
          description: The six-month price change.
        oneYearPriceChange:
          type: number
          description: The one-year price change.
        currMonthPriceChange:
          type: number
          description: The current month price change.
        currQuarterPriceChange:
          type: number
          description: The current quarter price change.
        currYearPriceChange:
          type: number
          description: The current year price change.
        lastYearPriceChange:
          type: number
          description: The last year price change.
        lastTwoYearsPriceChange:
          type: number
          description: The last two years price change.
        oneMonthAgoPriceChange:
          type: number
          description: The price change from one month ago.
        twoMonthsAgoPriceChange:
          type: number
          description: The price change from two months ago.
        threeMonthsAgoPriceChange:
          type: number
          description: The price change from three months ago.
        sixMonthsAgoPriceChange:
          type: number
          description: The price change from six months ago.
        oneYearAgoPriceChange:
          type: number
          description: The price change from one year ago.
        cvtBid:
          type: number
          description: The converted bid price.
        cvtAsk:
          type: number
          description: The converted ask price.
        cvtBiNoSpread:
          type: number
          description: The converted bid price without spread.
        cvtAskNoSpread:
          type: number
          description: The converted ask price without spread.
        traders7DayChange:
          type: number
          description: The change in the number of traders over the last 7 days.
        traders14DayChange:
          type: number
          description: The change in the number of traders over the last 14 days.
        traders30DayChange:
          type: number
          description: The change in the number of traders over the last 30 days.
        popularityUniques14Day:
          type: integer
          description: >-
            The number of unique users who viewed this instrument in the last 14
            days.
        popularityUniques30Day:
          type: integer
          description: >-
            The number of unique users who viewed this instrument in the last 30
            days.
        internalIndustryId:
          type: integer
          description: The internal industry ID.
        internalStockIndustryName:
          type: string
          description: The internal stock industry name.
        popularityUniques:
          type: integer
          description: Total number of unique users interested in this instrument.
        holdingPct:
          type: number
          description: The holding percentage of this instrument.
        buyHoldingPct:
          type: number
          description: The buy holding percentage.
        sellHoldingPct:
          type: number
          description: The sell holding percentage.
        buyPctChange24Hours:
          type: number
          description: The buy percentage change in the last 24 hours.
        absBuyPctChange24Hours:
          type: number
          description: The absolute buy percentage change in the last 24 hours.
        industryNameId:
          type: integer
          description: The industry name ID.
        sectorNameId:
          type: integer
          description: The sector name ID.
  securitySchemes:
    oauth2:
      type: oauth2
      description: >-
        eToro OAuth2. Each operation lists the scopes that grant access as
        separate `security` requirements (OpenAPI OR semantics): the caller's
        token only needs ONE of them — you do NOT need all of them. The same
        scopes back the x-api-key/x-user-key credential pair.
      flows:
        authorizationCode:
          authorizationUrl: ''
          tokenUrl: ''
          scopes:
            etoro-public:agent-portfolio:read: Grants access to the 'etoro-public:agent-portfolio:read' scope.
            etoro-public:agent-portfolio:write: Grants access to the 'etoro-public:agent-portfolio:write' scope.
            etoro-public:club:read: Grants access to the 'etoro-public:club:read' scope.
            etoro-public:demo:read: Grants access to the 'etoro-public:demo:read' scope.
            etoro-public:demo:write: Grants access to the 'etoro-public:demo:write' scope.
            etoro-public:feed:read: Grants access to the 'etoro-public:feed:read' scope.
            etoro-public:feed:write: Grants access to the 'etoro-public:feed:write' scope.
            etoro-public:market-data:read: Grants access to the 'etoro-public:market-data:read' scope.
            etoro-public:money.balance:read: Grants access to the 'etoro-public:money.balance:read' scope.
            etoro-public:money.cash-transactions:read: >-
              Grants access to the 'etoro-public:money.cash-transactions:read'
              scope.
            etoro-public:money.transfer:read: Grants access to the 'etoro-public:money.transfer:read' scope.
            etoro-public:money.transfer:write: Grants access to the 'etoro-public:money.transfer:write' scope.
            etoro-public:money.withdraw.crypto:read: >-
              Grants access to the 'etoro-public:money.withdraw.crypto:read'
              scope.
            etoro-public:money.withdraw.crypto:write: >-
              Grants access to the 'etoro-public:money.withdraw.crypto:write'
              scope.
            etoro-public:money:transfer: Grants access to the 'etoro-public:money:transfer' scope.
            etoro-public:notifications:read: Grants access to the 'etoro-public:notifications:read' scope.
            etoro-public:notifications:write: Grants access to the 'etoro-public:notifications:write' scope.
            etoro-public:pi-data:read: Grants access to the 'etoro-public:pi-data:read' scope.
            etoro-public:price-alerts:read: Grants access to the 'etoro-public:price-alerts:read' scope.
            etoro-public:price-alerts:write: Grants access to the 'etoro-public:price-alerts:write' scope.
            etoro-public:real:read: Grants access to the 'etoro-public:real:read' scope.
            etoro-public:real:write: Grants access to the 'etoro-public:real:write' scope.
            etoro-public:sso-applications:read: Grants access to the 'etoro-public:sso-applications:read' scope.
            etoro-public:sso-applications:write: Grants access to the 'etoro-public:sso-applications:write' scope.
            etoro-public:sso-scopes:read: Grants access to the 'etoro-public:sso-scopes:read' scope.
            etoro-public:sso-scopes:write: Grants access to the 'etoro-public:sso-scopes:write' scope.
            etoro-public:sub-accounts:read: Grants access to the 'etoro-public:sub-accounts:read' scope.
            etoro-public:sub-accounts:write: Grants access to the 'etoro-public:sub-accounts:write' scope.
            etoro-public:trade.demo:read: Grants access to the 'etoro-public:trade.demo:read' scope.
            etoro-public:trade.demo:write: Grants access to the 'etoro-public:trade.demo:write' scope.
            etoro-public:trade.real:read: Grants access to the 'etoro-public:trade.real:read' scope.
            etoro-public:trade.real:write: Grants access to the 'etoro-public:trade.real:write' scope.
            etoro-public:user-info:read: Grants access to the 'etoro-public:user-info:read' scope.
            etoro-public:watchlist:read: Grants access to the 'etoro-public:watchlist:read' scope.
            etoro-public:watchlist:write: Grants access to the 'etoro-public:watchlist:write' scope.

````