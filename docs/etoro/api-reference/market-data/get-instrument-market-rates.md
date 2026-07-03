> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get instrument market rates

> **Rate limit:** 120 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `GET /api/v1/market-data/exchanges`
- `GET /api/v1/market-data/instrument-types`
- `GET /api/v1/market-data/instruments`
- `GET /api/v1/market-data/instruments/history/closing-price`
- `GET /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}`
- `GET /api/v1/market-data/search`
- `GET /api/v1/market-data/stocks-industries`

---

Provides real-time market data including bid/ask prices, conversion rates, and execution prices for specified financial instruments. Essential for price discovery and trade execution decisions.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/market-data/instruments/rates
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
  /api/v1/market-data/instruments/rates:
    get:
      tags:
        - Market Data
      summary: Get instrument market rates
      description: >-
        **Rate limit:** 120 requests per 60 seconds. This is a **shared quota**
        — the same budget is consumed by a group of related endpoints, so
        calling any of them reduces what is left for the others (you cannot call
        each at the full rate independently). Endpoints sharing this quota:

        - `GET /api/v1/market-data/exchanges`

        - `GET /api/v1/market-data/instrument-types`

        - `GET /api/v1/market-data/instruments`

        - `GET /api/v1/market-data/instruments/history/closing-price`

        - `GET
        /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}`

        - `GET /api/v1/market-data/search`

        - `GET /api/v1/market-data/stocks-industries`


        ---


        Provides real-time market data including bid/ask prices, conversion
        rates, and execution prices for specified financial instruments.
        Essential for price discovery and trade execution decisions.
      operationId: getMarketDataInstrumentsRates
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: a040d420-c4d0-4293-b6a4-dc102344eeb7
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
        - name: instrumentIds
          in: query
          style: form
          description: >-
            Comma-separated list of instrument IDs to retrieve market rates for.
            Each ID represents a unique tradable asset in the system.
          explode: false
          schema:
            type: array
            items:
              type: integer
              format: int32
            maxItems: 100
          example: 1,2,3
          required: true
      responses:
        '200':
          description: Successfully retrieved current market rates
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LiveRatesResponse'
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
        '400':
          description: >-
            Invalid request - Typically due to invalid instrument IDs or
            exceeding maximum limit
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
            - etoro-public:trade.real:read
        - oauth2:
            - etoro-public:trade.real:write
        - oauth2:
            - etoro-public:market-data:read
components:
  schemas:
    LiveRatesResponse:
      type: object
      description: Container for real-time market rates data
      properties:
        rates:
          type: array
          description: Array of current market rates for requested instruments
          items:
            type: object
            description: Individual instrument rate information
            properties:
              instrumentID:
                type: integer
                description: Unique identifier for the financial instrument
              ask:
                type: number
                format: float
                description: >-
                  Current asking price (offer) for the instrument. This is the
                  price at which you can buy the asset.
              bid:
                type: number
                format: float
                description: >-
                  Current bid price for the instrument. This is the price at
                  which you can sell the asset.
              lastExecution:
                type: number
                format: float
                description: Price of the most recent trade execution for this instrument
              conversionRateAsk:
                type: number
                format: float
                description: >-
                  Current conversion rate (ask) from instrument's currency to
                  USD, used for position value calculations
              conversionRateBid:
                type: number
                format: float
                description: >-
                  Current conversion rate (bid) from instrument's currency to
                  USD, used for position value calculations
              date:
                type: string
                format: date-time
                description: The date-time of the price in the system
              unitMargin:
                type: number
                format: float
                description: (Obsolete) USD equivalent of the instrument price
              unitMarginAsk:
                type: number
                format: float
                description: (Obsolete) USD equivalent of the instrument ask price
              unitMarginBid:
                type: number
                format: float
                description: (Obsolete) USD equivalent of the instrument bid price
              priceRateID:
                type: integer
              bidDiscounted:
                type: number
                format: float
                description: Obsolete
              askDiscounted:
                type: number
                format: float
                description: Obsolete
              unitMarginBidDiscounted:
                type: number
                format: float
                description: Obsolete
              unitMarginAskDiscounted:
                type: number
                format: float
                description: Obsolete
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