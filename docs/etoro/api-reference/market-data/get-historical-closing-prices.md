> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get historical closing prices

> **Rate limit:** 120 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `GET /api/v1/market-data/exchanges`
- `GET /api/v1/market-data/instrument-types`
- `GET /api/v1/market-data/instruments`
- `GET /api/v1/market-data/instruments/rates`
- `GET /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}`
- `GET /api/v1/market-data/search`
- `GET /api/v1/market-data/stocks-industries`



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/market-data/instruments/history/closing-price
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
  /api/v1/market-data/instruments/history/closing-price:
    get:
      tags:
        - Market Data
      summary: Get historical closing prices
      description: >-
        **Rate limit:** 120 requests per 60 seconds. This is a **shared quota**
        — the same budget is consumed by a group of related endpoints, so
        calling any of them reduces what is left for the others (you cannot call
        each at the full rate independently). Endpoints sharing this quota:

        - `GET /api/v1/market-data/exchanges`

        - `GET /api/v1/market-data/instrument-types`

        - `GET /api/v1/market-data/instruments`

        - `GET /api/v1/market-data/instruments/rates`

        - `GET
        /api/v1/market-data/instruments/{instrumentId}/history/candles/{direction}/{interval}/{candlesCount}`

        - `GET /api/v1/market-data/search`

        - `GET /api/v1/market-data/stocks-industries`
      operationId: getClosingPrices
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 65ab2a46-0c1b-4e0b-99f3-d0d055eda74a
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
      responses:
        '200':
          description: Successful retrieval of closing prices
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/closingPricesResponse'
              example:
                - instrumentId: 1002
                  officialClosingPrice: 175.75
                  isMarketOpen: true
                  closingPrices:
                    daily:
                      price: 175.75
                      date: '2025-03-07 00:00:00Z'
                    weekly:
                      price: 175.75
                      date: '2025-03-07 00:00:00Z'
                    monthly:
                      price: 172.22
                      date: '2025-02-28 00:00:00Z'
                - instrumentId: 999
                  officialClosingPrice: 68
                  isMarketOpen: false
                  closingPrices:
                    daily:
                      price: 68
                      date: '2024-11-16 00:00:00Z'
                    weekly:
                      price: 68
                      date: '2024-11-16 00:00:00Z'
                    monthly:
                      price: -1
                      date: '0001-01-01 00:00:00Z'
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
    closingPricesResponse:
      type: array
      description: List of closing prices for all instruments
      items:
        type: object
        description: Closing price information for a specific instrument
        properties:
          instrumentId:
            type: integer
            description: Unique identifier of the instrument
          officialClosingPrice:
            type: number
            format: float
            description: Most recent official closing price for the instrument
          isMarketOpen:
            type: boolean
            description: Obsolete - Do not use
          closingPrices:
            type: object
            description: Historical closing prices at different time intervals
            properties:
              daily:
                type: object
                description: Official closing price from the previous trading day
                properties:
                  price:
                    type: number
                    format: float
                    description: Closing price value
                  date:
                    type: string
                    format: date-time
                    description: Date and time of the closing price in ISO 8601 format
              weekly:
                type: object
                description: Official closing price from the previous trading week
                properties:
                  price:
                    type: number
                    format: float
                    description: Closing price value
                  date:
                    type: string
                    format: date-time
                    description: Date and time of the closing price in ISO 8601 format
              monthly:
                type: object
                description: Official closing price from the previous trading month
                properties:
                  price:
                    type: number
                    format: float
                    description: >-
                      Closing price value. A value of -1 indicates no data
                      available.
                  date:
                    type: string
                    format: date-time
                    description: >-
                      Date and time of the closing price in ISO 8601 format.
                      Default date (0001-01-01) indicates no data available.
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