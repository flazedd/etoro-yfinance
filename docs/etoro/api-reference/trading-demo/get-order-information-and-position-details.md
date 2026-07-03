> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get order information and position details

> **Rate limit:** 60 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `GET /api/v1/trading/info/demo/orders/{orderId}`

---

Retrieves comprehensive information about a specific order, including the order status, execution details, and all positions that were opened or closed from this order. This endpoint is essential for tracking order execution and identifying which positions were created as a result of a specific order request. The response includes detailed position information with PositionID values that can be used to query position-specific details. Provide exactly one of orderId or referenceId.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v2/trading/info/demo/orders:lookup
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
  /api/v2/trading/info/demo/orders:lookup:
    get:
      tags:
        - Trading Demo
      summary: Get order information and position details
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is a **shared quota** —
        the same budget is consumed by a group of related endpoints, so calling
        any of them reduces what is left for the others (you cannot call each at
        the full rate independently). Endpoints sharing this quota:

        - `GET /api/v1/trading/info/demo/orders/{orderId}`


        ---


        Retrieves comprehensive information about a specific order, including
        the order status, execution details, and all positions that were opened
        or closed from this order. This endpoint is essential for tracking order
        execution and identifying which positions were created as a result of a
        specific order request. The response includes detailed position
        information with PositionID values that can be used to query
        position-specific details. Provide exactly one of orderId or
        referenceId.
      operationId: lookupDemoOrder
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 5604d3b5-ae13-43cb-8ef0-4417db36b9f8
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
        - name: orderId
          in: query
          description: Numeric order identifier. Mutually exclusive with referenceId.
          schema:
            type: integer
            format: int64
        - name: referenceId
          in: query
          description: >-
            Request ID header sent during order submission. Mutually exclusive
            with orderId.
          schema:
            type: string
      responses:
        '200':
          description: Order information retrieved successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetOrderInfoResponse'
              example:
                accountId: 7765437
                gcid: 987654321
                portfolioId: 1
                orderId: 13902598
                action: open
                transaction: buy
                type: mkt
                etoroOrderTypeId: 17
                status:
                  id: 1
                  name: Executed
                  errorCode: 0
                  errorMessage: null
                asset:
                  symbol: AAPL
                  instrumentId: 101
                  currency: USD
                  settlementType: cfd
                  leverage: 2
                  side: long
                orderCurrency: usd
                requestedAmount: 1000
                requestedUnits: null
                requestedContracts: null
                frozenAmount: 1002.5
                requestedTriggerRate: null
                openStopLossRate: 1.2
                openTakeProfitRate: 1.5
                stopLossType: fixed
                totalCosts: 2.5
                positionsToClose: []
                positionExecutions:
                  - positionId: 9001
                    state: open
                    investedAmountCurrency: 1000
                    initialExposureAccountCurrency: 1000
                    initialExposureAssetCurrency: 1000
                    addedFunds: 0
                    marginAccountCurrency: 1000
                    marginAssetCurrency: 1000
                    remainingUnits: 10.5
                    remainingContracts: 10.5
                    stopLossRate: 1.2
                    takeProfitRate: 1.5
                    openingData:
                      openTime: '2024-01-01T09:00:00Z'
                      orderId: 5001
                      executionTime: '2024-01-01T09:00:01Z'
                      units: 10.5
                      contracts: null
                      avgPrice: 95.238095
                      avgConversionRate: 1
                      marketSpread: 0.0002
                      markup: 0
                      priceId: 9876543210
                      fees: 2.5
                      taxes: 0
                requestTime: '2024-01-01T09:00:00Z'
                lastUpdate: '2024-01-01T09:00:01Z'
                openActionType: customer
                requestType: byUnits
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 2 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
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
          description: Order not found.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'
        '429':
          description: >-
            Too Many Requests — the shared rate limit (60 requests / 60s) was
            exceeded.
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 2 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
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
            - etoro-public:demo:read
        - oauth2:
            - etoro-public:demo:write
        - oauth2:
            - etoro-public:trade.demo:read
        - oauth2:
            - etoro-public:trade.demo:write
components:
  schemas:
    GetOrderInfoResponse:
      type: object
      description: >-
        Detailed information about a specific order retrieved via the orders
        lookup endpoint.
      properties:
        accountId:
          type: integer
          format: int64
          description: The account identifier associated with this order.
        gcid:
          type: integer
          format: int64
          description: The global customer identifier.
        portfolioId:
          type: integer
          format: int32
          description: The portfolio identifier.
        orderId:
          type: integer
          format: int64
          description: The unique identifier of the order.
        action:
          type: string
          description: 'The order action. Possible values: open, close.'
        transaction:
          type: string
          description: >-
            The transaction direction. Possible values: buy, sell, sellShort,
            buyToCover.
        type:
          type: string
          description: 'The order type. Possible values: mkt, mit.'
        etoroOrderTypeId:
          type: integer
          format: int32
          description: The internal eToro order type identifier.
        status:
          $ref: '#/components/schemas/GetOrderInfoStatus'
        asset:
          $ref: '#/components/schemas/GetOrderInfoAsset'
        orderCurrency:
          type: string
          description: The currency used for the order.
        requestedAmount:
          type: number
          format: double
          nullable: true
          description: The requested monetary amount for the order.
        requestedUnits:
          type: number
          format: double
          nullable: true
          description: The requested number of units for the order.
        requestedContracts:
          type: number
          format: double
          nullable: true
          description: The requested number of contracts for the order.
        frozenAmount:
          type: number
          format: double
          nullable: true
          description: The amount frozen/reserved for the order including costs.
        requestedTriggerRate:
          type: number
          format: double
          nullable: true
          description: The trigger rate for limit or stop orders.
        openStopLossRate:
          type: number
          format: double
          nullable: true
          description: The stop-loss rate at order open.
        openTakeProfitRate:
          type: number
          format: double
          nullable: true
          description: The take-profit rate at order open.
        stopLossType:
          type: string
          nullable: true
          description: 'The stop-loss type. Possible values: fixed, trailing.'
        totalCosts:
          type: number
          format: double
          description: Total costs associated with the order.
        positionsToClose:
          type: array
          items:
            type: integer
            format: int64
          description: List of position IDs to close as part of a close order.
        positionExecutions:
          type: array
          items:
            $ref: '#/components/schemas/GetOrderInfoPositionExecution'
          description: List of position executions resulting from this order.
        requestTime:
          type: string
          format: date-time
          description: The timestamp when the order was requested.
        lastUpdate:
          type: string
          format: date-time
          description: The timestamp of the last update to the order.
        openActionType:
          type: string
          description: The action type that initiated the order.
        requestType:
          type: string
          description: >-
            The request sizing type. Possible values: byAmount, byUnits,
            byContracts.
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
    GetOrderInfoStatus:
      type: object
      description: Status information for the order.
      properties:
        id:
          type: integer
          format: int32
          description: >-
            Status identifier. Common values: 1 = Executed, 2 = Cancelled, 3 =
            Rejected.
        name:
          type: string
          description: Human-readable status name.
        errorCode:
          type: integer
          format: int32
          description: Error code if the order failed. Zero indicates no error.
        errorMessage:
          type: string
          nullable: true
          description: Human-readable error message if the order failed.
    GetOrderInfoAsset:
      type: object
      description: Asset information associated with the order.
      properties:
        symbol:
          type: string
          description: The asset ticker symbol.
        instrumentId:
          type: integer
          format: int32
          description: The eToro instrument identifier.
        currency:
          type: string
          description: The asset's base currency.
        settlementType:
          type: string
          description: >-
            Settlement type. Possible values: cfd, real, realFutures,
            marginTrade.
        leverage:
          type: integer
          format: int32
          description: The leverage applied to the order.
        side:
          type: string
          description: 'The position side. Possible values: long, short.'
    GetOrderInfoPositionExecution:
      type: object
      description: Details of a position execution resulting from the order.
      properties:
        positionId:
          type: integer
          format: int64
          description: The unique identifier of the executed position.
        state:
          type: string
          description: 'The current state of the position. Possible values: open, closed.'
        investedAmountCurrency:
          type: number
          format: double
          description: The invested amount in the account currency.
        initialExposureAccountCurrency:
          type: number
          format: double
          description: The initial exposure in the account currency.
        initialExposureAssetCurrency:
          type: number
          format: double
          description: The initial exposure in the asset currency.
        addedFunds:
          type: number
          format: double
          description: Additional funds added to the position.
        marginAccountCurrency:
          type: number
          format: double
          description: Margin held in the account currency.
        marginAssetCurrency:
          type: number
          format: double
          description: Margin held in the asset currency.
        remainingUnits:
          type: number
          format: double
          description: Remaining units in the position.
        remainingContracts:
          type: number
          format: double
          nullable: true
          description: Remaining contracts in the position.
        stopLossRate:
          type: number
          format: double
          nullable: true
          description: The stop-loss rate for the position.
        takeProfitRate:
          type: number
          format: double
          nullable: true
          description: The take-profit rate for the position.
        openingData:
          $ref: '#/components/schemas/GetOrderInfoOpeningData'
    GetOrderInfoOpeningData:
      type: object
      description: Execution data recorded when the position was opened.
      properties:
        openTime:
          type: string
          format: date-time
          description: The timestamp when the position was opened.
        orderId:
          type: integer
          format: int64
          description: The order identifier that opened the position.
        executionTime:
          type: string
          format: date-time
          description: The execution timestamp.
        units:
          type: number
          format: double
          nullable: true
          description: Number of units executed.
        contracts:
          type: number
          format: double
          nullable: true
          description: Number of contracts executed.
        avgPrice:
          type: number
          format: double
          description: The average execution price.
        avgConversionRate:
          type: number
          format: double
          description: The average currency conversion rate applied.
        marketSpread:
          type: number
          format: double
          description: The market spread at execution time.
        markup:
          type: number
          format: double
          description: The markup applied to the spread.
        priceId:
          type: integer
          format: int64
          description: The price snapshot identifier used for execution.
        fees:
          type: number
          format: double
          description: Fees charged for the execution.
        taxes:
          type: number
          format: double
          description: Taxes applied to the execution.
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