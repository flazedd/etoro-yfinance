> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Search users

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Powerful search platform that enables advanced user discovery with comprehensive filtering capabilities. Supports complex queries across multiple dimensions including performance metrics, risk profiles, investment patterns, and account characteristics. Ideal for identifying users based on specific trading behaviors and performance criteria.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/user-info/people/search
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
  /api/v1/user-info/people/search:
    get:
      tags:
        - Users Info
      summary: Search users
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Powerful search platform that enables advanced user discovery with
        comprehensive filtering capabilities. Supports complex queries across
        multiple dimensions including performance metrics, risk profiles,
        investment patterns, and account characteristics. Ideal for identifying
        users based on specific trading behaviors and performance criteria.
      operationId: getUserInfoPeopleSearch
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 70918bcc-5606-46c4-8735-82a0f3978834
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
        - name: period
          in: query
          description: >-
            Defines the time period for analyzing user metrics and performance
            data. Supports various predefined intervals for consistent analysis.
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
          example: LastYear
        - name: isTestAccount
          in: query
          description: >-
            When set to true, filters results to include only test/demo
            accounts. When false, shows only live accounts. Optional filter.
          required: false
          schema:
            type: boolean
          example: false
        - name: optIn
          in: query
          description: >-
            Filter for users who have explicitly opted in to specific features
            or programs. Used for compliance and feature-specific filtering.
          required: false
          schema:
            type: boolean
          example: true
        - name: blocked
          in: query
          description: >-
            When true, includes only blocked accounts in the results. Used for
            compliance and risk management purposes.
          required: false
          schema:
            type: boolean
          example: false
        - name: page
          in: query
          description: Page number for pagination.
          required: false
          schema:
            type: integer
            example: 1
        - name: pageSize
          in: query
          description: Number of results per page.
          required: false
          schema:
            type: integer
            example: 10
        - name: sort
          in: query
          description: Sort results by specific field (e.g., -copiers).
          required: false
          schema:
            type: string
            example: '-copiers'
        - name: popularInvestor
          in: query
          description: Filter for popular investors.
          required: false
          schema:
            type: boolean
        - name: gainMax
          in: query
          description: Max gain value filter.
          required: false
          schema:
            type: integer
            example: 100
        - name: maxDailyRiskScoreMin
          in: query
          description: Minimum daily risk score.
          required: false
          schema:
            type: integer
            example: 1
        - name: maxDailyRiskScoreMax
          in: query
          description: Maximum daily risk score.
          required: false
          schema:
            type: integer
            example: 7
        - name: maxMonthlyRiskScoreMin
          in: query
          description: Minimum monthly risk score.
          required: false
          schema:
            type: integer
            example: 1
        - name: maxMonthlyRiskScoreMax
          in: query
          description: Maximum monthly risk score.
          required: false
          schema:
            type: integer
            example: 6
        - name: weeksSinceRegistrationMin
          in: query
          description: Minimum weeks since registration.
          required: false
          schema:
            type: integer
            example: 75
        - name: countryId
          in: query
          description: The registered country ID of the user
          required: false
          schema:
            type: integer
            example: 101
        - name: instrumentId
          in: query
          description: >-
            The instrument ID (you can also use this to exclude an instrument
            e.g., -5).
          required: false
          schema:
            type: integer
            example: -5
        - name: instrumentPctMin
          in: query
          description: Minimum percentage of investment in the requested instrument ID.
          required: false
          schema:
            type: integer
            example: 100
        - name: instrumentPctMax
          in: query
          description: Maximum percentage of investment in the requested instrument ID.
          required: false
          schema:
            type: integer
            example: 100
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  totalItems:
                    type: integer
                  items:
                    type: array
                    items:
                      type: object
                      properties:
                        customerId:
                          type: integer
                        userName:
                          type: string
                        fullName:
                          type: string
                        hasAvatar:
                          type: boolean
                        isSocialConnected:
                          type: boolean
                        isTestAccount:
                          type: boolean
                        displayFullName:
                          type: boolean
                        bonusOnly:
                          type: boolean
                        blocked:
                          type: boolean
                        verified:
                          type: boolean
                        popularInvestor:
                          type: boolean
                        copyBlock:
                          type: boolean
                        isFund:
                          type: boolean
                        isBronze:
                          type: boolean
                        fundType:
                          type: integer
                        tags:
                          type: array
                          items:
                            type: integer
                        gain:
                          type: number
                          format: float
                        dailyGain:
                          type: number
                          format: float
                        thisWeekGain:
                          type: number
                          format: float
                        riskScore:
                          type: integer
                        maxDailyRiskScore:
                          type: integer
                        maxMonthlyRiskScore:
                          type: integer
                        copiers:
                          type: integer
                        copiedTrades:
                          type: integer
                        copyTradesPct:
                          type: number
                          format: float
                        copyInvestmentPct:
                          type: number
                          format: float
                        baseLineCopiers:
                          type: integer
                        copiersGain:
                          type: number
                          format: float
                        aumTier:
                          type: integer
                        aumTierV2:
                          type: integer
                        aumTierDesc:
                          type: string
                          nullable: true
                        virtualCopiers:
                          type: integer
                        trades:
                          type: integer
                        winRatio:
                          type: number
                          format: float
                        dailyDd:
                          type: number
                          format: float
                        weeklyDd:
                          type: number
                          format: float
                        profitableWeeksPct:
                          type: number
                          format: float
                        profitableMonthsPct:
                          type: number
                          format: float
                        velocity:
                          type: number
                          format: float
                        exposure:
                          type: number
                          format: float
                        avgPosSize:
                          type: number
                          format: float
                        optimalCopyPosSize:
                          type: number
                          format: float
                        highLeveragePct:
                          type: number
                          format: float
                        mediumLeveragePct:
                          type: number
                          format: float
                        lowLeveragePct:
                          type: number
                          format: float
                        peakToValley:
                          type: number
                          format: float
                        peakToValleyStart:
                          type: string
                          format: date-time
                        peakToValleyEnd:
                          type: string
                          format: date-time
                        longPosPct:
                          type: number
                          format: float
                        topTradedInstrumentId:
                          type: integer
                        topTradedAssetClassId:
                          type: integer
                        topTradedInstrumentPct:
                          type: number
                          format: float
                        totalTradedInstruments:
                          type: integer
                        activeWeeks:
                          type: integer
                        firstActivity:
                          type: integer
                          description: >-
                            Number of days since the beginning of the interval
                            of a user's first trading activity
                        lastActivity:
                          type: integer
                          description: >-
                            Number of days from the last trading activity till
                            the end of the interval
                        activeWeeksPct:
                          type: number
                          format: float
                        weeksSinceRegistration:
                          type: integer
                        country:
                          type: string
                        affiliateId:
                          type: integer
                        instrumentPct:
                          type: number
                          format: float
                        countryId:
                          type: integer
                          description: The registered country ID of the user
                        isPopularInvestor:
                          type: boolean
                          description: Indicates if the user is a popular investor
                        topTradedAssetId:
                          type: integer
                          description: Top traded asset class ID in this interval
                required:
                  - totalItems
                  - items
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