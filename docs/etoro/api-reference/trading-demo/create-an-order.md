> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create an order

> **Rate limit:** 20 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `DELETE /api/v1/trading/execution/demo/limit-orders/{orderId}`
- `DELETE /api/v1/trading/execution/demo/market-close-orders/{orderId}`
- `DELETE /api/v1/trading/execution/demo/market-open-orders/{orderId}`
- `DELETE /api/v2/trading/execution/demo/orders/{orderId}`
- `POST /api/v1/trading/execution/demo/limit-orders`
- `POST /api/v1/trading/execution/demo/market-close-orders/positions/{positionId}`
- `POST /api/v1/trading/execution/demo/market-open-orders/by-amount`
- `POST /api/v1/trading/execution/demo/market-open-orders/by-units`

---

This endpoint allows traders to place an order. Leverage, stop-loss, and take-profit settings can be applied. Order size must use exactly one of amount, units, or contracts. For open orders the instrument must be identified by exactly one of symbol or instrumentId - providing both is rejected. A unique X-Request-Id header (GUID) is required for idempotency. Currently only orders to open a position are supported.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v2/trading/execution/demo/orders
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
  /api/v2/trading/execution/demo/orders:
    post:
      tags:
        - Trading Demo
      summary: Create an order
      description: >-
        **Rate limit:** 20 requests per 60 seconds. This is a **shared quota** —
        the same budget is consumed by a group of related endpoints, so calling
        any of them reduces what is left for the others (you cannot call each at
        the full rate independently). Endpoints sharing this quota:

        - `DELETE /api/v1/trading/execution/demo/limit-orders/{orderId}`

        - `DELETE /api/v1/trading/execution/demo/market-close-orders/{orderId}`

        - `DELETE /api/v1/trading/execution/demo/market-open-orders/{orderId}`

        - `DELETE /api/v2/trading/execution/demo/orders/{orderId}`

        - `POST /api/v1/trading/execution/demo/limit-orders`

        - `POST
        /api/v1/trading/execution/demo/market-close-orders/positions/{positionId}`

        - `POST /api/v1/trading/execution/demo/market-open-orders/by-amount`

        - `POST /api/v1/trading/execution/demo/market-open-orders/by-units`


        ---


        This endpoint allows traders to place an order. Leverage, stop-loss, and
        take-profit settings can be applied. Order size must use exactly one of
        amount, units, or contracts. For open orders the instrument must be
        identified by exactly one of symbol or instrumentId - providing both is
        rejected. A unique X-Request-Id header (GUID) is required for
        idempotency. Currently only orders to open a position are supported.
      operationId: createDemoOrder
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: d7334dd0-9b31-4d26-9e08-79664144b792
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
            example:
              action: open
              transaction: buy
              symbol: null
              instrumentId: 101
              settlementType: cfd
              orderType: mkt
              triggerRate: null
              leverage: 2
              amount: 1000
              orderCurrency: usd
              units: null
              contracts: null
              stopLossRate: 1.2
              takeProfitRate: 1.5
              stopLossType: fixed
              additionalMargin: null
              positionIds: null
      responses:
        '200':
          description: Order submitted successfully. Returns the created order details.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnifiedOrderResponse'
              example:
                token: 066faaee-e1e9-49d2-a568-c6e1cc336ad8
                orderId: 13902598
                referenceId: 1c94300c-90aa-4303-9d00-dec376d74efb
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 9 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
              schema:
                type: integer
              example: 20
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
              example: 20;w=60
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
          description: Resource not found.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'
        '429':
          description: >-
            Too Many Requests — the shared rate limit (20 requests / 60s) was
            exceeded.
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 9 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
              schema:
                type: integer
              example: 20
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
              example: 20;w=60
            Retry-After:
              description: Seconds to wait before retrying.
              schema:
                type: integer
              example: 60
        '500':
          description: Internal server error.
      security:
        - oauth2:
            - etoro-public:demo:write
        - oauth2:
            - etoro-public:trade.demo:write
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
    UnifiedOrderResponse:
      type: object
      description: Response payload after successfully submitting an order.
      properties:
        token:
          type: string
          format: uuid
          description: >-
            A tracking token for the order request, used for correlation and
            debugging.
          example: 066faaee-e1e9-49d2-a568-c6e1cc336ad8
        orderId:
          type: integer
          format: int64
          description: The unique identifier of the created order.
          example: 13902598
        referenceId:
          type: string
          format: uuid
          description: >-
            The client reference identifier for the order, matching the
            X-Request-Id header if provided.
          example: 1c94300c-90aa-4303-9d00-dec376d74efb
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