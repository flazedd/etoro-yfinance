> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get market exposure history

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Returns daily directional exposure breakdown per instrument for a publicly visible portfolio. Data is only available for investors who have not opted out - opted-out portfolios return 403 for third-party callers. Callers must authenticate with their own token. Use period OR minDate+maxDate (mutually exclusive). All values are decimal fractions of total daily investment: 0.5 = 50%. Simulated positions are excluded.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v2/portfolios/{username}/exposure/history
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
  /api/v2/portfolios/{username}/exposure/history:
    get:
      tags:
        - User Stats
      summary: Get market exposure history
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Returns daily directional exposure breakdown per instrument for a
        publicly visible portfolio. Data is only available for investors who
        have not opted out - opted-out portfolios return 403 for third-party
        callers. Callers must authenticate with their own token. Use period OR
        minDate+maxDate (mutually exclusive). All values are decimal fractions
        of total daily investment: 0.5 = 50%. Simulated positions are excluded.
      operationId: getExposureHistory
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 08ed2155-5ac9-4cac-9cd9-cb4444b55682
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
        - name: username
          in: path
          required: true
          schema:
            type: string
          description: The eToro username of the portfolio owner.
        - name: period
          in: query
          required: false
          schema:
            $ref: '#/components/schemas/RankingPeriod'
          description: Predefined rolling window. Mutually exclusive with minDate/maxDate.
          x-mutual-exclusivity-group: dateFilter
        - name: minDate
          in: query
          required: false
          schema:
            type: string
            format: date
          description: >-
            Start date inclusive (ISO 8601 date, YYYY-MM-DD). Mutually exclusive
            with period. Required together with maxDate when period is omitted.
          x-mutual-exclusivity-group: dateFilter
        - name: maxDate
          in: query
          required: false
          schema:
            type: string
            format: date
          description: >-
            End date inclusive (ISO 8601 date, YYYY-MM-DD). Mutually exclusive
            with period. Required together with minDate when period is omitted.
          x-mutual-exclusivity-group: dateFilter
        - name: count
          in: query
          required: false
          schema:
            type: integer
            minimum: 0
          description: >-
            Downsample time axis to at most N buckets. Omit or pass 0 for no
            downsampling.
      responses:
        '200':
          description: Successful response
          headers:
            Cache-Control:
              description: >-
                public, max-age=3600 for opted-in users; private, max-age=3600
                for opted-out self-view.
              schema:
                type: string
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This is the
                default shared pool used by every endpoint without a dedicated
                limit, so it is NOT per-endpoint — requests across those
                endpoints all draw from this one budget.
              schema:
                type: integer
              example: 60
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
              example: 60;w=60
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExposureHistoryResponse'
              example:
                userName: john.smith
                results:
                  - date: '2024-01-31'
                    absExposurePct: 0.72
                    exposureItems:
                      - instrumentId: 1001
                        symbol: AAPL
                        netExposurePct: 0.43
                        absExposurePct: 0.43
                      - instrumentId: 2005
                        symbol: TSLA
                        netExposurePct: -0.25
                        absExposurePct: 0.25
        '400':
          description: Invalid request parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatsExposureApi_Error'
        '401':
          description: Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatsExposureApi_Error'
        '403':
          description: Target user has opted out of portfolio exposure
          headers:
            Cache-Control:
              description: no-store
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatsExposureApi_Error'
        '404':
          description: Resource not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatsExposureApi_Error'
        '429':
          description: >-
            Too Many Requests — the shared rate limit (60 requests / 60s) was
            exceeded.
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This is the
                default shared pool used by every endpoint without a dedicated
                limit, so it is NOT per-endpoint — requests across those
                endpoints all draw from this one budget.
              schema:
                type: integer
              example: 60
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
              example: 60;w=60
            Retry-After:
              description: Seconds to wait before retrying.
              schema:
                type: integer
              example: 60
        '502':
          description: Upstream service returned an error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatsExposureApi_Error'
        '504':
          description: Upstream service timed out
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StatsExposureApi_Error'
      security:
        - oauth2:
            - etoro-public:user-info:read
components:
  schemas:
    RankingPeriod:
      type: string
      enum:
        - CurrMonth
        - OneMonthAgo
        - TwoMonthsAgo
        - CurrQuarter
        - ThreeMonthsAgo
        - SixMonthsAgo
        - CurrYear
        - OneYearAgo
        - LastYear
        - LastTwoYears
    ExposureHistoryResponse:
      type: object
      required:
        - userName
        - results
      properties:
        userName:
          type: string
        results:
          type: array
          description: Daily snapshots ordered ascending by date.
          items:
            $ref: '#/components/schemas/ExposureHistoryEntry'
    StatsExposureApi_Error:
      type: object
      required:
        - success
        - timestamp
        - requestId
      properties:
        success:
          type: boolean
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: string
            field:
              type: string
            value:
              type: string
        timestamp:
          type: string
          format: date-time
        requestId:
          type: string
    ExposureHistoryEntry:
      type: object
      required:
        - date
        - absExposurePct
        - exposureItems
      properties:
        date:
          type: string
          format: date
          description: ISO 8601 date of this snapshot (YYYY-MM-DD)
        absExposurePct:
          type: number
          description: >-
            Sum of absolute exposure across all instruments as a ratio of total
            daily investment. Decimal fraction: 0.5 = 50%.
        exposureItems:
          type: array
          description: Per-instrument exposure breakdown
          items:
            $ref: '#/components/schemas/ExposureItem'
    ExposureItem:
      type: object
      required:
        - instrumentId
        - symbol
        - netExposurePct
        - absExposurePct
      properties:
        instrumentId:
          type: integer
        symbol:
          type: string
          description: Trading symbol for this instrument (e.g. AAPL, TSLA)
        netExposurePct:
          type: number
          description: >-
            Net exposure for this instrument as a ratio of total equity. Signed
            - positive = long, negative = short. Decimal fraction: 0.5 = 50%.
        absExposurePct:
          type: number
          description: >-
            Absolute exposure for this instrument as a ratio of total equity.
            Always positive. Decimal fraction: 0.5 = 50%.
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