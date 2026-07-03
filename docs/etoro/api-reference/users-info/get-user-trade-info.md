> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get user trade info

> **Rate limit:** 60 requests per 60 seconds. This is a **dedicated** limit for this endpoint — it is **not shared** with (pooled across) any other endpoint, so the full rate is available to this endpoint alone.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/user-info/people/{username}/tradeinfo
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
  /api/v1/user-info/people/{username}/tradeinfo:
    get:
      tags:
        - Users Info
      summary: Get user trade info
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is a **dedicated**
        limit for this endpoint — it is **not shared** with (pooled across) any
        other endpoint, so the full rate is available to this endpoint alone.
      operationId: getUserInfoPeopleByUsernameTradeinfo
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 5d25b7a5-c6c0-432b-af9d-19933418fa07
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
          description: The username of the user to retrieve the discovery info for.
          in: path
          schema:
            type: string
          required: true
        - name: period
          in: query
          description: The period filter (e.g., LastTwoYears).
          required: true
          schema:
            type: string
            enum:
              - CurrMonth
              - CurrQuarter
              - CurrYear
              - LastYear
              - LastTwoYears
              - OneMonthAgo
              - TwoMonthsAgo
              - ThreeMonthsAgo
              - SixMonthsAgo
              - OneYearAgo
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  userName:
                    type: string
                    description: The username of the customer
                  fullName:
                    type: string
                    description: Full name of the customer
                  weeksSinceRegistration:
                    type: integer
                    description: Number of weeks since registration
                  countryId:
                    type: integer
                    description: The registered country ID of the user
                  affiliateId:
                    type: integer
                    description: The affiliate ID of the user
                  isPopularInvestor:
                    type: boolean
                    description: Is the customer a popular investor
                  isFund:
                    type: boolean
                    description: Does this customer represent a fund
                  hasAvatar:
                    type: boolean
                    description: Does the customer have a picture
                  gain:
                    type: number
                    format: float
                    description: The periodic gain of the user
                  dailyGain:
                    type: number
                    format: float
                    description: The user's last day gain
                  thisWeekGain:
                    type: number
                    format: float
                    description: The user's gain from the beginning of the trading week
                  riskScore:
                    type: integer
                    description: The current risk score of the user
                  maxDailyRiskScore:
                    type: integer
                    description: The maximum daily risk score of the user in this interval
                  maxMonthlyRiskScore:
                    type: integer
                    description: >-
                      The maximum monthly risk score of the user in this
                      interval
                  copiers:
                    type: integer
                    description: The current number of copiers of this user
                  copiedTrades:
                    type: integer
                    description: The total number of copied trades in this interval
                  copyTradesPct:
                    type: number
                    format: float
                    description: >-
                      The percentage of copied trades in this interval of all
                      trades
                  copyInvestmentPct:
                    type: number
                    format: float
                    description: >-
                      The percentage of invested amounts in copied trades in
                      this interval of all investments
                  baseLineCopiers:
                    type: integer
                    description: The number of copiers one week ago
                  copiersGain:
                    type: number
                    format: float
                    description: The gain percentage of the number of copiers in a week
                  aumTier:
                    type: integer
                    description: >-
                      The total assets under management of the user, in a scale
                      of 0-4, where 4 is the highest tier
                  aumTierDesc:
                    type: string
                    description: Description of the AUM Tier
                  fundType:
                    type: integer
                    description: Fund Type
                  virtualCopiers:
                    type: integer
                    description: The total amount of virtual copiers of this user
                  trades:
                    type: integer
                    description: The total number of trades in this interval
                  topTradedInstrumentId:
                    type: integer
                    description: Top Traded Instrument ID in this interval
                  topTradedAssetId:
                    type: integer
                    description: Top Traded Asset ID in this interval
                  winRatio:
                    type: number
                    format: float
                    description: The winning ratio of all closed trades in this interval
                  dailyDd:
                    type: number
                    format: float
                    description: The maximum daily draw-down of the user in this interval
                  weeklyDd:
                    type: number
                    format: float
                    description: The maximum weekly draw-down of this user in this interval
                  peakToValley:
                    type: number
                    format: float
                    description: The peak to valley draw-down in this interval
                  profitableWeeksPct:
                    type: number
                    format: float
                    description: >-
                      The percentage of trading weeks which were profitable in
                      this interval
                  profitableMonthsPct:
                    type: number
                    format: float
                    description: >-
                      The percentage of months which were profitable in this
                      interval
                  avgPosSize:
                    type: number
                    format: float
                    description: >-
                      Average position size relative to the realized equity on
                      opening the trade
                  highLeveragePct:
                    type: number
                    format: float
                    description: High leverage trades percentage in this interval
                  mediumLeveragePct:
                    type: number
                    format: float
                    description: Medium leverage trades percentage in this interval
                  lowLeveragePct:
                    type: number
                    format: float
                    description: Low leverage trades percentage in this interval
                  firstActivity:
                    type: integer
                    description: >-
                      Number of days since the beginning of the interval of a
                      user trading activity
                  lastActivity:
                    type: integer
                    description: >-
                      Number of days from the last trading activity till the end
                      of the interval
                  activeWeeksPct:
                    type: number
                    format: float
                    description: >-
                      The percentage of weeks in the interval which the user had
                      active trades
                  instrumentPct:
                    type: number
                    format: float
                    description: Percentage of investment in the requested instrument ID
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This limit is
                dedicated to this endpoint — it is not shared with (pooled
                across) any other endpoint.
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
        '429':
          description: Too Many Requests — the rate limit (60 requests / 60s) was exceeded.
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This limit is
                dedicated to this endpoint — it is not shared with (pooled
                across) any other endpoint.
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
            - etoro-public:user-info:read
components:
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