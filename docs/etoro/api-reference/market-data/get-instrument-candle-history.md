> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get instrument candle history

> **Rate limit:** 120 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `GET /api/v1/market-data/exchanges`
- `GET /api/v1/market-data/instrument-types`
- `GET /api/v1/market-data/instruments`
- `GET /api/v1/market-data/instruments/history/closing-price`
- `GET /api/v1/market-data/instruments/rates`
- `GET /api/v1/market-data/search`
- `GET /api/v1/market-data/stocks-industries`

---

Retrieves historical price data in OHLCV (Open, High, Low, Close, Volume) format for a specified instrument. The data is organized into time-based candles of various intervals, from one minute to one week.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}
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
  /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}:
    get:
      tags:
        - Market Data
      summary: Get instrument candle history
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

        - `GET /api/v1/market-data/search`

        - `GET /api/v1/market-data/stocks-industries`


        ---


        Retrieves historical price data in OHLCV (Open, High, Low, Close,
        Volume) format for a specified instrument. The data is organized into
        time-based candles of various intervals, from one minute to one week.
      operationId: getCandles
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 6e6a895f-a7aa-4b0e-8d93-0ad5616baf88
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
        - name: direction
          in: path
          description: >-
            Sorting direction of the candles data. Use 'asc' for oldest to
            newest, or 'desc' for newest to oldest.
          required: true
          schema:
            type: string
            enum:
              - asc
              - desc
        - name: interval
          in: path
          description: >-
            Time interval for each candle. Determines the granularity of the
            price data. Shorter intervals provide more detailed price action but
            require more data points.
          required: true
          schema:
            type: string
            enum:
              - OneMinute
              - FiveMinutes
              - TenMinutes
              - FifteenMinutes
              - ThirtyMinutes
              - OneHour
              - FourHours
              - OneDay
              - OneWeek
        - name: candlesCount
          in: path
          description: >-
            Number of candles to retrieve. Maximum value is 1000. For longer
            historical periods, consider using a larger time interval or making
            multiple requests.
          required: true
          schema:
            type: integer
            default: 100
            maximum: 1000
        - name: instrumentId
          in: path
          description: >-
            Unique identifier of the financial instrument to retrieve candles
            for. This ID is consistent across all eToro systems.
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Successful retrieval of candles data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/candlesResponse'
              example:
                interval: OneMinute
                candles:
                  - instrumentId: 12
                    candles:
                      - instrumentID: 12
                        fromDate: '2025-03-05T10:34:00Z'
                        open: 1.70227
                        high: 1.70277
                        low: 1.70221
                        close: 1.70253
                        volume: 0
                      - instrumentID: 12
                        fromDate: '2025-03-05T10:35:00Z'
                        open: 1.70252
                        high: 1.70276
                        low: 1.70244
                        close: 1.70276
                        volume: 0
                    rangeOpen: 1.70227
                    rangeClose: 1.70276
                    rangeHigh: 1.70277
                    rangeLow: 1.70221
                    volume: 0
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
    candlesResponse:
      type: object
      description: Response containing historical price data in candlestick format
      properties:
        interval:
          type: string
          description: >-
            Time interval of the returned candles. Matches the interval
            parameter from the request.
          enum:
            - OneMinute
            - FiveMinutes
            - TenMinutes
            - FifteenMinutes
            - ThirtyMinutes
            - OneHour
            - FourHours
            - OneDay
            - OneWeek
        candles:
          type: array
          description: List of candle data grouped by instrument
          items:
            type: object
            description: Candle data for a specific instrument
            properties:
              instrumentId:
                type: integer
                description: Identifier of the instrument these candles belong to
              candles:
                type: array
                description: List of individual candles representing price action over time
                items:
                  type: object
                  description: Individual candle data point
                  properties:
                    instrumentID:
                      type: integer
                      description: Identifier of the instrument this candle belongs to
                    fromDate:
                      type: string
                      format: date-time
                      description: Start time of the candle period in ISO 8601 format
                    open:
                      type: number
                      format: float
                      description: Opening price at the start of the candle period
                    high:
                      type: number
                      format: float
                      description: Highest price reached during the candle period
                    low:
                      type: number
                      format: float
                      description: Lowest price reached during the candle period
                    close:
                      type: number
                      format: float
                      description: Closing price at the end of the candle period
                    volume:
                      type: number
                      format: float
                      description: Trading volume during the candle period
              rangeOpen:
                type: number
                format: float
                description: Opening price of the first candle in the range
              rangeClose:
                type: number
                format: float
                description: Closing price of the last candle in the range
              rangeHigh:
                type: number
                format: float
                description: Highest price across all candles in the range
              rangeLow:
                type: number
                format: float
                description: Lowest price across all candles in the range
              volume:
                type: number
                format: float
                description: Total trading volume across all candles in the range
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