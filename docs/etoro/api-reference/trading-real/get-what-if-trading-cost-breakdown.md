> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get what-if trading cost breakdown

> **Rate limit:** 60 requests per 60 seconds. This is a **dedicated** limit for this endpoint — it is **not shared** with (pooled across) any other endpoint, so the full rate is available to this endpoint alone.

---

Returns the markup, market spread, transaction fee, overnight fee, over-weekend fee, and SDRT that would apply if the supplied order were executed now. For `action: open`, exactly one of `symbol` or `instrumentId` must be provided and `leverage` must be at least 1. For `action: close`, `positionIds` must be non-empty.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v2/trading/info/costs
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
  /api/v2/trading/info/costs:
    post:
      tags:
        - Trading Real
      summary: Get what-if trading cost breakdown
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is a **dedicated**
        limit for this endpoint — it is **not shared** with (pooled across) any
        other endpoint, so the full rate is available to this endpoint alone.


        ---


        Returns the markup, market spread, transaction fee, overnight fee,
        over-weekend fee, and SDRT that would apply if the supplied order were
        executed now. For `action: open`, exactly one of `symbol` or
        `instrumentId` must be provided and `leverage` must be at least 1. For
        `action: close`, `positionIds` must be non-empty.
      operationId: getCost
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 44c92ccc-209b-4592-92a1-94ca2771dc42
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
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UnifiedOrderRequest'
            examples:
              open:
                summary: Cost for opening a position
                value:
                  action: open
                  transaction: buy
                  instrumentId: 101
                  settlementType: cfd
                  orderType: mkt
                  leverage: 2
                  amount: 1000
                  orderCurrency: usd
              close:
                summary: Cost for closing one or more positions
                value:
                  action: close
                  transaction: sell
                  positionIds:
                    - 13902598
                    - 13902599
      responses:
        '200':
          description: Cost breakdown resolved successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetCostResponse'
              example:
                instrumentId: 101
                symbol: AAPL
                costs:
                  - costType: markup
                    amount: 0.15
                    currency: USD
                  - costType: marketSpread
                    amount: 0.03
                    currency: USD
                  - costType: transactionFee
                    amount: 1
                    currency: USD
                  - costType: overnightFee
                    amount: 0.25
                    currency: USD
                  - costType: overWeekendFee
                    amount: 0.75
                    currency: USD
                  - costType: sdrt
                    amount: 0.5
                    currency: USD
                lastUpdated: '2026-05-25T08:30:00Z'
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
        '400':
          description: Invalid request. Validation failed.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'
        '401':
          description: Unauthorized. Invalid or missing authentication.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'
        '404':
          description: Instrument or position not found.
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
        '500':
          description: Internal server error.
      security:
        - oauth2:
            - etoro-public:real:read
        - oauth2:
            - etoro-public:real:write
        - oauth2:
            - etoro-public:trade.real:read
        - oauth2:
            - etoro-public:trade.real:write
components:
  schemas:
    UnifiedOrderRequest:
      type: object
      description: Request payload for creating an order to open or close a position.
      required:
        - action
        - transaction
      properties:
        action:
          type: string
          description: 'The order action type. Possible values: open, close.'
          enum:
            - open
            - close
          example: open
        transaction:
          type: string
          description: >-
            The transaction direction. Possible values: buy, sell, sellShort,
            buyToCover.
          enum:
            - buy
            - sell
            - sellShort
            - buyToCover
          example: buy
        symbol:
          type: string
          description: >-
            The asset ticker symbol. For open orders provide exactly one of
            symbol or instrumentId - providing both is rejected.
          nullable: true
          example: AAPL
        instrumentId:
          type: integer
          format: int32
          description: >-
            The eToro instrument identifier. For open orders provide exactly one
            of symbol or instrumentId - providing both is rejected.
          nullable: true
          example: 101
        settlementType:
          type: string
          description: >-
            The settlement type. Possible values: cfd, real, realFutures,
            marginTrade. Required for open orders.
          nullable: true
          enum:
            - cfd
            - real
            - realFutures
            - marginTrade
          example: cfd
        orderType:
          type: string
          description: >-
            The order execution type. Possible values: mkt (market), mit (market
            if touched).
          enum:
            - mkt
            - mit
          example: mkt
        triggerRate:
          type: number
          format: double
          nullable: true
          description: The trigger rate for mit orders. Required for mit orders.
        leverage:
          type: integer
          format: int32
          description: The leverage multiplier to apply. Required for open orders.
          nullable: true
          example: 2
        amount:
          type: number
          format: double
          nullable: true
          description: >-
            The monetary amount to invest in the order currency. Mutually
            exclusive with units and contracts.
          example: 1000
        orderCurrency:
          type: string
          description: The currency for the order amount. Typically usd.
          nullable: true
          example: usd
        units:
          type: number
          format: double
          nullable: true
          description: >-
            The number of units to trade. Mutually exclusive with amount and
            contracts.
        contracts:
          type: number
          format: double
          nullable: true
          description: >-
            The number of contracts to trade. Mutually exclusive with amount and
            units.
        stopLossRate:
          type: number
          format: double
          nullable: true
          description: The stop-loss rate at which the position will automatically close.
          example: 1.2
        takeProfitRate:
          type: number
          format: double
          nullable: true
          description: The take-profit rate at which the position will automatically close.
          example: 1.5
        stopLossType:
          type: string
          nullable: true
          description: 'The stop-loss type. Possible values: fixed, trailing.'
          enum:
            - fixed
            - trailing
          example: fixed
        additionalMargin:
          type: number
          format: double
          nullable: true
          description: Additional margin to allocate to the position.
        positionIds:
          type: array
          items:
            type: integer
            format: int64
          nullable: true
          description: List of position IDs to close. Required for close orders.
    GetCostResponse:
      type: object
      description: Cost breakdown for a hypothetical open or close order.
      properties:
        instrumentId:
          type: integer
          format: int32
          description: Identifier of the instrument the cost breakdown applies to.
        symbol:
          type: string
          nullable: true
          description: Symbol of the instrument
        costs:
          type: array
          items:
            $ref: '#/components/schemas/CostBreakdown'
          description: Cost components that would apply to the proposed order.
        lastUpdated:
          type: string
          format: date-time
          description: Timestamp (ISO 8601) at which the cost figures were generated.
    ProblemDetails:
      type: object
      properties:
        type:
          type: string
          nullable: true
        title:
          type: string
          nullable: true
        status:
          type: integer
          format: int32
          nullable: true
        detail:
          type: string
          nullable: true
        instance:
          type: string
          nullable: true
      additionalProperties: {}
    CostBreakdown:
      type: object
      description: >-
        Individual cost component (markup, fees, SDRT) in the requested order
        currency.
      properties:
        costType:
          type: string
          description: Identifies which cost component this entry represents.
          enum:
            - markup
            - marketSpread
            - transactionFee
            - overnightFee
            - overWeekendFee
            - sdrt
        amount:
          type: number
          format: double
          description: The monetary value of this cost component, expressed in `currency`.
        currency:
          type: string
          description: ISO 4217 currency code in which `amount` is denominated.
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