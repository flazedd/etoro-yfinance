> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get demo portfolio breakdown

> **Rate limit:** 60 requests per 60 seconds. This is a **dedicated** limit for this endpoint — it is **not shared** with (pooled across) any other endpoint, so the full rate is available to this endpoint alone.

---

Returns detailed portfolio information including active positions, pending orders, mirror trading details, and account balances. This endpoint provides a complete overview of the user's trading activity and current market exposure.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/trading/info/demo/portfolio
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
  /api/v1/trading/info/demo/portfolio:
    get:
      tags:
        - Trading Demo
      summary: Get demo portfolio breakdown
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is a **dedicated**
        limit for this endpoint — it is **not shared** with (pooled across) any
        other endpoint, so the full rate is available to this endpoint alone.


        ---


        Returns detailed portfolio information including active positions,
        pending orders, mirror trading details, and account balances. This
        endpoint provides a complete overview of the user's trading activity and
        current market exposure.
      operationId: getPortfolioDemo
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: df8ccdf6-320a-4b83-9ba1-5b12b16a820d
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
          description: Successfully retrieved portfolio information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PortfolioResponse'
              example:
                clientPortfolio:
                  positions:
                    - positionID: 2150896073
                      CID: 7765437
                      openDateTime: '2024-08-01T07:44:26.103Z'
                      openRate: 2020.7784
                      instrumentID: 1002
                      isBuy: true
                      takeProfitRate: 0
                      stopLossRate: 0.0001
                      mirrorID: 0
                      parentPositionID: 0
                      amount: 100
                      leverage: 1
                      orderID: 12402059
                      orderType: 17
                      units: 0.049485
                      totalFees: 0
                      initialAmountInDollars: 100
                      isTslEnabled: false
                      stopLossVersion: 3
                      isSettled: true
                      redeemStatusID: 0
                      initialUnits: 0.049485
                      isPartiallyAltered: false
                      unitsBaseValueDollars: 100
                      isDiscounted: true
                      openPositionActionType: 0
                      settlementTypeID: 1
                      isDetached: false
                      openConversionRate: 1
                      pnlVersion: 1
                      totalExternalFees: 0
                      totalExternalTaxes: 0
                      isNoTakeProfit: true
                      isNoStopLoss: true
                      lotCount: 0.049485
                  credit: 280.35
                  mirrors:
                    - mirrorID: 1841334
                      CID: 7765437
                      parentCID: 14370798
                      stopLossPercentage: 5
                      isPaused: false
                      copyExistingPositions: true
                      availableAmount: 560
                      stopLossAmount: 28
                      initialInvestment: 560
                      depositSummary: 0
                      withdrawalSummary: 0
                      positions: []
                      entryOrders: []
                      exitOrders: []
                      parentUsername: Deposit158990700
                      closedPositionsNetProfit: 0
                      startedCopyDate: '2024-05-23T13:31:57.007Z'
                      pendingForClosure: false
                      parentMirrors: []
                      mirrorCalculationType: 1
                      ordersForOpen: []
                      ordersForClose: []
                      ordersForCloseMultiple: []
                      delayedOrderForClose: []
                      delayedOrderForOpen: []
                      mirrorStatusId: 0
                  orders:
                    - orderID: 5669649
                      CID: 7765437
                      openDateTime: '2024-06-06T08:07:25.083Z'
                      instrumentID: 100043
                      isBuy: true
                      takeProfitRate: 0
                      stopLossRate: 0.00001
                      rate: 0.1453
                      amount: 100
                      leverage: 1
                      units: 688.231246
                      isTslEnabled: false
                      executionType: 0
                      isDiscounted: false
                  stockOrders: []
                  entryOrders: []
                  exitOrders: []
                  ordersForOpen: []
                  ordersForClose: []
                  ordersForCloseMultiple: []
                  bonusCredit: 0
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
            - etoro-public:demo:read
        - oauth2:
            - etoro-public:demo:write
        - oauth2:
            - etoro-public:trade.demo:read
        - oauth2:
            - etoro-public:trade.demo:write
components:
  schemas:
    PortfolioResponse:
      type: object
      description: >-
        Comprehensive portfolio information including positions, orders, and
        account status
      properties:
        clientPortfolio:
          type: object
          description: Container for all portfolio-related information
          properties:
            positions:
              type: array
              description: List of currently open trading positions
              items:
                $ref: '#/components/schemas/TradingDemoApi_Position'
            credit:
              type: number
              format: float
              description: >-
                Available trading balance in USD, representing funds available
                for new positions
            mirrors:
              type: array
              description: Copy trading configurations and positions
              items:
                type: object
                description: Individual mirror trading setup
                properties:
                  mirrorID:
                    type: integer
                    description: Unique identifier for the mirror trading configuration
                  CID:
                    type: integer
                    description: Customer ID associated with the mirror
                  parentCID:
                    type: integer
                    description: Customer ID of the trader being copied
                  stopLossPercentage:
                    type: number
                    format: float
                    description: >-
                      The precentage of the mirror value that the StopLossAmount
                      represented at the time of the last edit. Adding or
                      removing funds from the mirror will trigger recalculation
                      of StopLossAmount based on this value compared to the
                      current mirror value
                  isPaused:
                    type: boolean
                    description: >-
                      Indication if the mirror is currently paused, restricting
                      open of additional positions inside the mirror
                  copyExistingPositions:
                    type: boolean
                    description: >-
                      Indication if mirror originally copied all parent existing
                      position on mirror registration
                  availableAmount:
                    type: number
                    format: float
                    description: >-
                      Available to trade USD balance in the mirror. This balance
                      is reserved for mirror operations
                  stopLossAmount:
                    type: number
                    format: float
                    description: >-
                      USD value of the mirror at which MirrorStopLoss will be
                      triggered and cause liquidation of the mirror. Adding or
                      removing funds from the mirror will trigger recalculation
                      of this value based on StopLossPercentage compared to the
                      current mirror value
                  initialInvestment:
                    type: number
                    format: float
                    description: USD amount initially invested in the mirror
                  depositSummary:
                    type: number
                    format: float
                    description: >-
                      Total USD amount deposited into the mirror after initial
                      investment
                  withdrawalSummary:
                    type: number
                    format: float
                    description: Total USD amount withdrawn from the mirror
                  positions:
                    type: array
                    description: Positions within this copy trading mirror
                    items:
                      $ref: '#/components/schemas/TradingDemoApi_Position'
                  entryOrders:
                    type: array
                    description: Obsolete
                    items:
                      type: object
                  exitOrders:
                    type: array
                    description: Obsolete
                    items:
                      type: object
                  parentUsername:
                    type: string
                    description: Username of the trader being copied
                  closedPositionsNetProfit:
                    type: number
                    format: float
                    description: >-
                      Total USD net profit of all positions that closed in the
                      mirror
                  startedCopyDate:
                    type: string
                    format: date-time
                    description: Date and time when the mirror trading was initiated
                  pendingForClosure:
                    type: boolean
                    description: Indication if the mirror is in closure process
                  parentMirrors:
                    type: array
                    items:
                      type: object
                  mirrorCalculationType:
                    type: integer
                    description: >-
                      (Obsolete) Mirror positions weights calculation
                      methodology
                  ordersForOpen:
                    type: array
                    description: Active orders in the mirror to open positions
                    items:
                      type: object
                  ordersForClose:
                    type: array
                    description: Active orders in the mirror to close positions
                    items:
                      type: object
                  ordersForCloseMultiple:
                    type: array
                    description: Active orders in the mirror to close positions
                    items:
                      type: object
                  delayedOrderForClose:
                    type: array
                    description: Obsolete
                    items:
                      type: object
                  delayedOrderForOpen:
                    type: array
                    description: Obsolete
                    items:
                      type: object
                  mirrorStatusID:
                    type: integer
                    description: >-
                      Current status of the mirror. 0 - Active, 1 - Paused, 2 -
                      Pending Closure, 3 - In Alignment Process
            orders:
              type: array
              description: List of pending orders
              items:
                type: object
                description: Individual order details
                properties:
                  orderID:
                    type: integer
                    description: Unique identifier for the order
                  CID:
                    type: integer
                    description: Customer ID associated with the order
                  openDateTime:
                    type: string
                    format: date-time
                    description: Date and time when the order was created
                  instrumentID:
                    type: integer
                    description: Identifier of the instrument being traded
                  isBuy:
                    type: boolean
                    description: Direction of the position. true - Long, false - Short
                  takeProfitRate:
                    type: number
                    format: float
                    description: >-
                      The take-profit trigger price at which the position will
                      generate a Market Order to close (after it has opened).
                      TakeProfit trigger price must be better than the current
                      price.
                  stopLossRate:
                    type: number
                    format: float
                    description: >-
                      The stop-loss trigger price at which the position will
                      generate a Market Order to close (after it was opened).
                      StopLoss trigger price must be worse than current price.
                  rate:
                    type: number
                    format: float
                    description: Asset rate at which to send market order to the market
                  amount:
                    type: number
                    format: float
                    description: USD amount to invest in the position
                  leverage:
                    type: number
                    format: float
                    description: Leverage multiplier to apply to the position
                  units:
                    type: number
                    format: float
                    description: >-
                      Units to open the position. If this value is greater than
                      zero the position will open on the requested units, and
                      not amount
                  isTslEnabled:
                    type: boolean
                    description: >-
                      Indicates if a trailing stop loss (TSL) is enabled. This
                      means that the stoploss rate indicated will get updated
                      automatically whenever the asset price increases (for long
                      positions) or decreases (for short position) effectively
                      keeping the stoploss in a constant gap from the best price
                      achieved so far.
                  executionType:
                    type: integer
                    description: Type of order execution
                  isDiscounted:
                    type: boolean
                    description: Obsolete
            stockOrders:
              type: array
              description: Obsolete
              items:
                type: object
            entryOrders:
              type: array
              description: Obsolete
              items:
                type: object
            exitOrders:
              type: array
              description: Obsolete
              items:
                type: object
            ordersForOpen:
              type: array
              description: Active orders to open positions
              items:
                type: object
            ordersForClose:
              type: array
              description: Active orders to close positions
              items:
                type: object
            ordersForCloseMultiple:
              type: array
              description: Active orders to close multiple positions
              items:
                type: object
            bonusCredit:
              type: number
              format: float
              description: Bonus credit amount in USD available for trading
    TradingDemoApi_Position:
      type: object
      description: Individual position details
      properties:
        positionID:
          type: integer
          description: Unique identifier for the position
        CID:
          type: integer
          description: Customer ID associated with the position
        openDateTime:
          type: string
          format: date-time
          description: Timestamp when the position was opened in ISO 8601 format
        openRate:
          type: number
          format: float
          description: Entry price of the position in the instrument's currency
        instrumentID:
          type: integer
          description: Identifier of the traded instrument
        mirrorID:
          type: integer
          description: Mirror ID if the position is part of copy trading, 0 otherwise
        parentPositionID:
          type: integer
          description: Parent position ID for mirrored positions, 0 otherwise
        isBuy:
          type: boolean
          description: >-
            Position direction: true for long (buy) positions, false for short
            (sell) positions
        leverage:
          type: number
          format: float
          description: Leverage multiplier applied to the position
        takeProfitRate:
          type: number
          format: float
          description: >-
            The take-profit trigger price at which the position will generate a
            Market Order to close (after it has opened). TakeProfit trigger
            price must be better than the current price.
        stopLossRate:
          type: number
          format: float
          description: >-
            The stop-loss trigger price at which the position will generate a
            Market Order to close (after it was opened). StopLoss trigger price
            must be worse than current price.
        amount:
          type: number
          format: float
          description: >-
            USD amount allocated to the position. This amount includes both the
            initial investment, and additional margin allocated to the position
            as collateral
        orderID:
          type: integer
          description: >-
            Original orderID the position was opened by. Need to match together
            with orderType
        orderType:
          type: integer
          description: >-
            Original orderType of the order the position was opened by. Need to
            match together with orderID
        units:
          type: number
          format: float
          description: Number of units in the position
        totalFees:
          type: number
          format: float
          description: >-
            Total overnight fees and dividends charged/paid on the position in
            USD. Negative amount represents refund
        initialAmountInDollars:
          type: number
          format: float
          description: Initial investment USD amount in the position
        isTslEnabled:
          type: boolean
          description: Indication if TrailingStopLoss feature is active on this position
        stopLossVersion:
          type: integer
          description: >-
            Manual stop loss edit version. Each time StopLossRate is manually
            update this value is incremented
        isSettled:
          type: boolean
          description: Obsolete
        redeemStatusID:
          type: integer
          description: >-
            If the position is currently in redeem process, this value
            represents the current status
        initialUnits:
          type: number
          format: float
          description: Initial invested units in the position
        isPartiallyAltered:
          type: boolean
          description: Indication whether this position was partially closed
        unitsBaseValueDollars:
          type: number
          format: float
          description: Current units invested value in USD
        isDiscounted:
          type: boolean
          description: Obsolete
        openPositionActionType:
          type: integer
          description: Position open reason
        settlementTypeID:
          type: integer
          description: >-
            Position investment type. 0 - CFD, 1 - Real Asset, 2 - SWAP, 3 -
            Crypto MarginTrade, 4 - Future Contract
        isDetached:
          type: boolean
          description: >-
            Indication if the position was originally opened inside a mirror and
            detached from it
        openConversionRate:
          type: number
          format: float
          description: Conversion rate at position opening
        pnlVersion:
          type: integer
          description: Pnl formula used for calculating profit and loss
        totalExternalFees:
          type: number
          format: float
          description: >-
            Total fees in USD charged on the position. Example - TicketFee. This
            value does not include overnight fees and dividends
        totalExternalTaxes:
          type: number
          format: float
          description: Total taxes in USD charged on the position. Example - SDRT
        isNoTakeProfit:
          type: boolean
          description: >-
            Indication if TakeProfit is enabled for the position. false =
            enabled, true = disabled
        isNoStopLoss:
          type: boolean
          description: >-
            Indication if StopLoss is enabled for the position. false = enabled,
            true = disabled
        lotCount:
          type: number
          format: float
          description: >-
            Number of lots the position represents. For FutureContracts this
            value represents the number of contracts acquired
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