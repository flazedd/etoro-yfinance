> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get user live portfolio

> **Rate limit:** 60 requests per 60 seconds. This is a **dedicated** limit for this endpoint — it is **not shared** with (pooled across) any other endpoint, so the full rate is available to this endpoint alone.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/user-info/people/{username}/portfolio/live
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
  /api/v1/user-info/people/{username}/portfolio/live:
    get:
      tags:
        - Users Info
      summary: Get user live portfolio
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is a **dedicated**
        limit for this endpoint — it is **not shared** with (pooled across) any
        other endpoint, so the full rate is available to this endpoint alone.
      operationId: getUserInfoPeopleByUsernamePortfolioLive
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: a04b407e-796e-43d9-8431-669cf97e7297
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
          description: The username of the user to retrieve the live portfolio for.
          in: path
          schema:
            type: string
          required: true
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  realizedCreditPct:
                    type: number
                    format: decimal
                    description: Credit as a percentage of the realized credit
                  unrealizedCreditPct:
                    type: number
                    format: decimal
                    description: Credit as a percentage of the unrealized credit
                  positions:
                    type: array
                    items:
                      type: object
                      properties:
                        positionId:
                          type: integer
                          description: Position ID
                        openTimestamp:
                          type: string
                          format: date-time
                          description: Open Timestamp
                        openRate:
                          type: number
                          format: decimal
                          description: Open Rate
                        instrumentId:
                          type: integer
                          description: Instrument ID
                        isBuy:
                          type: boolean
                          description: Buy/Sell
                        leverage:
                          type: integer
                          description: Leverage
                        takeProfitRate:
                          type: number
                          format: decimal
                          description: Take Profit
                        stopLossRate:
                          type: number
                          format: decimal
                          description: Stop Loss
                        socialTradeId:
                          type: integer
                          description: Mirror ID
                        parentPositionId:
                          type: integer
                          description: Parent Position ID
                        investmentPct:
                          type: number
                          format: decimal
                          description: Realized Investment
                        netProfit:
                          type: number
                          format: decimal
                          description: Profit Percentage
                        trailingStopLoss:
                          type: boolean
                          description: Trailing Stop loss enabled
                  socialTrades:
                    type: array
                    items:
                      type: object
                      properties:
                        socialTradeId:
                          type: integer
                          description: Internal Mirror ID
                        parentUsername:
                          type: string
                          description: Parent Username
                        stopLossPercentage:
                          type: number
                          format: decimal
                          description: Stop Loss
                        openTimestamp:
                          type: string
                          format: date-time
                          description: Opening Timestamp
                        investmentPct:
                          type: number
                          format: decimal
                          description: Investment Pct
                        openInvestmentPct:
                          type: number
                          format: decimal
                          description: Open Trades in Mirror
                        netProfit:
                          type: number
                          format: decimal
                          description: Profit Pct
                        openNetProfit:
                          type: number
                          format: decimal
                          description: Net profit of opened trades
                        closedNetProfit:
                          type: number
                          format: decimal
                          description: Net profit of closed trades
                        realizedPct:
                          type: number
                          format: decimal
                          description: Live Realized percentage
                        unrealizedPct:
                          type: number
                          format: decimal
                          description: Unrealized
                        isClosing:
                          type: boolean
                          description: Pending Close
                        positions:
                          type: array
                          items:
                            type: object
                            properties:
                              positionId:
                                type: integer
                                description: Position ID
                              openTimestamp:
                                type: string
                                format: date-time
                                description: Open Timestamp
                              openRate:
                                type: number
                                format: decimal
                                description: Open Rate
                              instrumentId:
                                type: integer
                                description: Instrument ID
                              isBuy:
                                type: boolean
                                description: Buy/Sell
                              leverage:
                                type: integer
                                description: Leverage
                              takeProfitRate:
                                type: number
                                format: decimal
                                description: Take Profit
                              stopLossRate:
                                type: number
                                format: decimal
                                description: Stop Loss
                              socialTradeId:
                                type: integer
                                description: Mirror ID
                              parentPositionId:
                                type: integer
                                description: Parent Position ID
                              investmentPct:
                                type: number
                                format: decimal
                                description: Realized Investment
                              netProfit:
                                type: number
                                format: decimal
                                description: Profit Percentage
                              trailingStopLoss:
                                type: boolean
                                description: Trailing Stop loss enabled
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