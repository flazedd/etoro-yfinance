> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get account PnL and portfolio details

> **Rate limit:** 60 requests per 60 seconds. This is a **dedicated** limit for this endpoint — it is **not shared** with (pooled across) any other endpoint, so the full rate is available to this endpoint alone.

---

Retrieves the real account's current portfolio, including credit, open positions, orders, mirrors, and PnL details.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/trading/info/real/pnl
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
  /api/v1/trading/info/real/pnl:
    get:
      tags:
        - Trading Real
      summary: Get account PnL and portfolio details
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is a **dedicated**
        limit for this endpoint — it is **not shared** with (pooled across) any
        other endpoint, so the full rate is available to this endpoint alone.


        ---


        Retrieves the real account's current portfolio, including credit, open
        positions, orders, mirrors, and PnL details.
      operationId: getRealAccountPnl
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 0d1f0e9b-676f-4d83-8c77-c9a492912cc4
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
          description: Successfully retrieved real account PnL and portfolio information.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PortfolioResponseWithPnl'
              example:
                clientPortfolio:
                  credit: 10000.5
                  unrealizedPnL: 251
                  mirrors:
                    - mirrorId: 1
                      cid: 123
                      parentCid: 456
                      stopLossPercentage: 15.5
                      isPaused: false
                      copyExistingPositions: true
                      availableAmount: 5000
                      stopLossAmount: 750
                      initialInvestment: 10000
                      depositSummary: 12000
                      withdrawalSummary: 2000
                      positions:
                        - positionId: 9002
                          cid: 124
                          openDateTime: '2024-01-02T09:00:00Z'
                          openRate: 1.2346
                          instrumentId: 102
                          isBuy: false
                          takeProfitRate: 1.6
                          stopLossRate: 1.1
                          mirrorId: 1
                          parentPositionId: 8002
                          amount: 2000
                          leverage: 3
                          orderId: 5002
                          orderType: 2
                          units: 20.5
                          totalFees: 3.5
                          initialAmountInDollars: 2000
                          isTslEnabled: true
                          stopLossVersion: 2
                          isSettled: false
                          redeemStatusId: 1
                          initialUnits: 20.5
                          isPartiallyAltered: true
                          unitsBaseValueDollars: 2000
                          isDiscounted: true
                          openPositionActionType: 2
                          settlementTypeId: 2
                          isDetached: true
                          openConversionRate: 1.2
                          pnlVersion: 2
                          totalExternalFees: 1
                          totalExternalTaxes: 0.5
                          isNoTakeProfit: true
                          isNoStopLoss: false
                          lotCount: 2
                          externalOperation: null
                          pnL: 150.75
                          closeRate: 1.3
                          closeConversionRate: 1.15
                          timestamp: '2024-01-02T12:00:00Z'
                      parentUsername: parent_user
                      closedPositionsNetProfit: 350.75
                      startedCopyDate: '2024-01-01T09:00:00Z'
                      pendingForClosure: false
                      parentMirrors: []
                      mirrorCalculationType: 2
                      ordersForOpen:
                        - orderId: 1001
                          orderType: 1
                          statusId: 1
                          cid: 123
                          openDateTime: '2024-01-01T09:00:00Z'
                          lastUpdate: '2024-01-02T10:00:00Z'
                          instrumentId: 101
                          amount: 1000
                          amountInUnits: 10.5
                          isBuy: true
                          leverage: 2
                          stopLossRate: 1.2345
                          takeProfitRate: 1.3456
                          isTslEnabled: false
                          isDiscounted: true
                          mirrorId: 1
                          frozenAmount: 0
                          totalExternalCosts: 5
                          isNoTakeProfit: false
                          isNoStopLoss: false
                          lotCount: 1
                          openPositionActionType: 1
                          externalOperation: null
                      ordersForClose:
                        - orderId: 2001
                          orderType: 2
                          statusId: 1
                          cid: 123
                          openDateTime: '2024-01-01T09:00:00Z'
                          lastUpdate: '2024-01-02T10:00:00Z'
                          instrumentId: 101
                          unitsToDeduct: 5
                          lotsToDeduct: 0.5
                          positionId: 3001
                      ordersForCloseMultiple:
                        - orderId: 3001
                          orderType: 3
                          statusId: 1
                          cid: 123
                          openDateTime: '2024-01-01T09:00:00Z'
                          lastUpdate: '2024-01-02T10:00:00Z'
                          instrumentId: 101
                          unitsToDeduct: 10
                          lotsToDeduct: 1
                          pendingClosePositionIds:
                            - 3001
                            - 3002
                      mirrorStatusId: 1
                  orders:
                    - orderId: 5001
                      cid: 123
                      openDateTime: '2024-01-01T09:00:00Z'
                      instrumentId: 101
                      isBuy: true
                      takeProfitRate: 1.5
                      stopLossRate: 1.2
                      rate: 1.3
                      amount: 1000
                      leverage: 2
                      units: 10.5
                      isTslEnabled: false
                      executionType: 1
                      isDiscounted: false
                      isNoTakeProfit: false
                      isNoStopLoss: false
                  ordersForOpen:
                    - orderId: 1001
                      orderType: 1
                      statusId: 1
                      cid: 123
                      openDateTime: '2024-01-01T09:00:00Z'
                      lastUpdate: '2024-01-02T10:00:00Z'
                      instrumentId: 101
                      amount: 1000
                      amountInUnits: 10.5
                      isBuy: true
                      leverage: 2
                      stopLossRate: 1.2345
                      takeProfitRate: 1.3456
                      isTslEnabled: false
                      isDiscounted: true
                      mirrorId: 1
                      frozenAmount: 0
                      totalExternalCosts: 5
                      isNoTakeProfit: false
                      isNoStopLoss: false
                      lotCount: 1
                      openPositionActionType: 1
                      externalOperation: null
                  ordersForClose:
                    - orderId: 2001
                      orderType: 2
                      statusId: 1
                      cid: 123
                      openDateTime: '2024-01-01T09:00:00Z'
                      lastUpdate: '2024-01-02T10:00:00Z'
                      instrumentId: 101
                      unitsToDeduct: 5
                      lotsToDeduct: 0.5
                      positionId: 3001
                  ordersForCloseMultiple:
                    - orderId: 3001
                      orderType: 3
                      statusId: 1
                      cid: 123
                      openDateTime: '2024-01-01T09:00:00Z'
                      lastUpdate: '2024-01-02T10:00:00Z'
                      instrumentId: 101
                      unitsToDeduct: 10
                      lotsToDeduct: 1
                      pendingClosePositionIds:
                        - 3001
                        - 3002
                  bonusCredit: 500
                  positions:
                    - positionId: 9001
                      cid: 123
                      openDateTime: '2024-01-01T09:00:00Z'
                      openRate: 1.2345
                      instrumentId: 101
                      isBuy: true
                      takeProfitRate: 1.5
                      stopLossRate: 1.2
                      mirrorId: 1
                      parentPositionId: 8001
                      amount: 1000
                      leverage: 2
                      orderId: 5001
                      orderType: 1
                      units: 10.5
                      totalFees: 2.5
                      initialAmountInDollars: 1000
                      isTslEnabled: false
                      stopLossVersion: 1
                      isSettled: true
                      redeemStatusId: 0
                      initialUnits: 10.5
                      isPartiallyAltered: false
                      unitsBaseValueDollars: 1000
                      isDiscounted: false
                      openPositionActionType: 1
                      settlementTypeId: 1
                      isDetached: false
                      openConversionRate: 1
                      pnlVersion: 1
                      totalExternalFees: 0
                      totalExternalTaxes: 0
                      isNoTakeProfit: false
                      isNoStopLoss: false
                      lotCount: 1
                      externalOperation: null
                      pnL: 100.25
                      closeRate: 1.25
                      closeConversionRate: 1.1
                      timestamp: '2024-01-01T12:00:00Z'
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
            - etoro-public:real:write
        - oauth2:
            - etoro-public:trade.real:read
        - oauth2:
            - etoro-public:trade.real:write
components:
  schemas:
    PortfolioResponseWithPnl:
      type: object
      description: >-
        Comprehensive portfolio information including positions, orders, and
        account status
      properties:
        clientPortfolio:
          $ref: '#/components/schemas/ClientPortfolio'
          description: Container for all portfolio-related information
    ClientPortfolio:
      type: object
      properties:
        positions:
          type: array
          items:
            $ref: '#/components/schemas/TradingRealAdminApi_Position'
          description: List of currently open trading positions
        credit:
          type: number
          format: float
          description: >-
            Available trading balance in USD, representing funds available for
            new actions
        mirrors:
          type: array
          items:
            $ref: '#/components/schemas/Mirror'
          description: Copy trading configurations and positions
        orders:
          type: array
          items:
            $ref: '#/components/schemas/TradingRealAdminApi_Order'
          description: List of pending orders
        ordersForOpen:
          type: array
          items:
            $ref: '#/components/schemas/OrderForOpen'
          description: Active orders to open positions
        ordersForClose:
          type: array
          items:
            $ref: '#/components/schemas/OrderForClose'
          description: Active orders to close positions
        ordersForCloseMultiple:
          type: array
          items:
            $ref: '#/components/schemas/OrderForCloseMultiple'
          description: Active orders to close multiple positions
        bonusCredit:
          type: number
          format: float
          description: Bonus credit amount in USD in the account
        unrealizedPnL:
          type: number
          format: float
          description: >-
            Total unrealized profit and loss across all open positions in the
            portfolio
        accountCurrencyId:
          type: integer
          description: Currency ID of the account (1 = USD)
        stockOrders:
          type: array
          items:
            type: object
          description: Stock-specific pending orders
        entryOrders:
          type: array
          items:
            type: object
          description: Entry orders awaiting execution
        exitOrders:
          type: array
          items:
            type: object
          description: Exit orders awaiting execution
    TradingRealAdminApi_Position:
      type: object
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
        takeProfitRate:
          type: number
          format: float
          description: >-
            Rate at which TakeProfit will trigger and send MarketOrder to close
            the position
        stopLossRate:
          type: number
          format: float
          description: >-
            Rate at which StopLoss will trigger and send MarketOrder to close
            the position
        amount:
          type: number
          format: float
          description: >-
            USD amount allocated to the position. This amount includes both the
            initial investment, and additional margin allocated to the position
            as collateral
        leverage:
          type: integer
          description: Leverage multiplier applied to the position
        orderID:
          type: integer
          description: >-
            Original orderID the position was opened by. Need to match together
            with orderType
        orderType:
          type: integer
          description: >-
            Original orderType of the order the position was opened by. Need to
            match together with orderId
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
          description: >-
            Initial investment USD amount in the position. This value does not
            change in case the position was partially closed
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
          description: >-
            Initial invested units in the position. This value does not change
            in case the position was partially closed
        isPartiallyAltered:
          type: boolean
          description: Indication whether this position was partially closed
        unitsBaseValueDollars:
          type: number
          format: float
          description: >-
            USD value of the current units in the position, based on the initial
            investment. If the position was not partially altered, this value
            equals initialAmountInDollars
        isDiscounted:
          type: boolean
          description: >-
            Obsolete. This value is used to indicate if the relevant prices for
            the position are Ask/Bid or AskDiscounted/BidDiscounted
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
          description: >-
            Conversion rate from the asset currency to USD at the time the
            position was opened
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
            Number of lots the position represents. For FutureContracts, this
            value represents the number of contracts acquired. This property is
            not relevant for instruments that are not futures instruments
        unrealizedPnL:
          type: object
          nullable: true
          description: >-
            Unrealized profit/loss details for the position (only present in PnL
            endpoints)
          properties:
            pnL:
              type: number
              format: float
              description: Unrealized P&L in account currency
            pnlAssetCurrency:
              type: number
              format: float
              description: Unrealized P&L in asset currency
            exposureInAccountCurrency:
              type: number
              format: float
              description: Current exposure in account currency
            exposureInAssetCurrency:
              type: number
              format: float
              description: Current exposure in asset currency
            marginInAccountCurrency:
              type: number
              format: float
              description: Margin in account currency
            marginInAssetCurrency:
              type: number
              format: float
              description: Margin in asset currency
            marginCurrencyId:
              type: integer
              description: Currency ID for margin
            assetCurrencyId:
              type: integer
              description: Currency ID for the asset
            closeRate:
              type: number
              format: float
              description: Current close rate
            closeConversionRate:
              type: number
              format: float
              description: Current close conversion rate
            timestamp:
              type: string
              format: date-time
              description: Timestamp of the PnL calculation
    Mirror:
      type: object
      properties:
        mirrorID:
          type: integer
          description: Unique identifier for the mirror
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
            represented at the time of the last edit. Adding or removing funds
            from the mirror will trigger recalculation of StopLossAmount based
            on this value compared to the current mirror value
        isPaused:
          type: boolean
          description: >-
            Indication if the mirror is currently paused, restricting open of
            additional positions inside the mirror
        copyExistingPositions:
          type: boolean
          description: >-
            Indication if mirror originally copied all parent existing position
            on mirror registration
        availableAmount:
          type: number
          format: float
          description: >-
            Available to trade USD balance in the mirror. This balance is
            reserved for mirror operations
        stopLossAmount:
          type: number
          format: float
          description: >-
            USD value of the mirror at which MirrorStopLoss will be triggered
            and cause liquidation of the mirror. Adding or removing funds from
            the mirror will trigger recalculation of this value based on
            StopLossPercentage compared to the current mirror value
        initialInvestment:
          type: number
          format: float
          description: USD amount initially invested in the mirror
        depositSummary:
          type: number
          format: float
          description: Total USD amount deposited into the mirror after initial investment
        withdrawalSummary:
          type: number
          format: float
          description: Total USD amount withdrawn from the mirror
        positions:
          type: array
          items:
            $ref: '#/components/schemas/TradingRealAdminApi_Position'
          description: List of currently open trading positions in the mirror
        parentUsername:
          type: string
          description: Username of the trader being copied
        closedPositionsNetProfit:
          type: number
          format: float
          description: Total USD net profit of all positions that closed in the mirror
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
          description: Parent mirrors for this mirror (if any)
        mirrorCalculationType:
          type: integer
          description: (Obsolete) Mirror positions weights calculation methodology
        ordersForOpen:
          type: array
          items:
            $ref: '#/components/schemas/OrderForOpen'
          description: Active orders in the mirror to open positions
        ordersForClose:
          type: array
          items:
            $ref: '#/components/schemas/OrderForClose'
          description: Active orders in the mirror to close positions
        ordersForCloseMultiple:
          type: array
          items:
            $ref: '#/components/schemas/OrderForCloseMultiple'
          description: Active orders in the mirror to close positions
        mirrorStatusID:
          type: integer
          description: >-
            Current status of the mirror. 0 - Active, 1 - Paused, 2 - Pending
            Closure, 3 - In Alignment Process
        delayedOrderForClose:
          type: array
          items:
            type: object
          description: Delayed orders for closing positions
        delayedOrderForOpen:
          type: array
          items:
            type: object
          description: Delayed orders for opening positions
        entryOrders:
          type: array
          items:
            type: object
          description: Entry orders awaiting execution in the mirror
        exitOrders:
          type: array
          items:
            type: object
          description: Exit orders awaiting execution in the mirror
    TradingRealAdminApi_Order:
      type: object
      properties:
        orderId:
          type: integer
          description: Unique identifier for the order
        cid:
          type: integer
          description: Customer ID associated with the order
        openDateTime:
          type: string
          format: date-time
          description: Date and time when the order was created
        instrumentId:
          type: integer
          description: Identifier of the instrument being traded
        isBuy:
          type: boolean
          description: Direction of the position. true - Long, false - Short
        takeProfitRate:
          type: number
          format: float
          description: >-
            Rate at which TakeProfit will trigger and send MarketOrder to close
            the position once it is open
        stopLossRate:
          type: number
          format: float
          description: >-
            Rate at which StopLoss will trigger and send MarketOrder to close
            the position once it is open
        rate:
          type: number
          format: float
          description: Asset rate at which to send market order to the market
        amount:
          type: number
          format: float
          description: USD amount to invest in the position
        leverage:
          type: integer
          description: Leverage multiplier to apply to the position
        units:
          type: number
          format: float
          description: >-
            Units to open the position. If this value is greater than zero the
            position will open on the requested units, and not amount
        isTslEnabled:
          type: boolean
          description: Indication if to enable TSL feature on the position once it is open
        executionType:
          type: integer
          description: Type of order execution
        isDiscounted:
          type: boolean
          description: Obsolete
        isNoTakeProfit:
          type: boolean
          description: >-
            Indication if TakeProfit is enabled for the order. false = enabled,
            true = disabled
        isNoStopLoss:
          type: boolean
          description: >-
            Indication if StopLoss is enabled for the order. false = enabled,
            true = disabled
    OrderForOpen:
      type: object
      properties:
        orderId:
          type: integer
          description: Unique identifier for the order
        orderType:
          type: integer
          description: Type of order executed
        statusId:
          type: integer
          description: Status of the order
        cid:
          type: integer
          description: Customer ID associated with the order
        openDateTime:
          type: string
          format: date-time
          description: The timestamp when the order was opened.
        lastUpdate:
          type: string
          format: date-time
          description: The last update timestamp of the order.
        instrumentId:
          type: integer
          description: The unique identifier of the financial instrument to trade.
        amount:
          type: number
          format: float
          description: The amount of money to invest in the trade.
        amountInUnits:
          type: number
          format: float
          description: The number of units to trade.
        isBuy:
          type: boolean
          description: True for a buy (long) order, false for a sell (short) order.
        leverage:
          type: integer
          description: The leverage multiplier for the trade.
        stopLossRate:
          type: number
          format: float
          description: >-
            The stop-loss rate at which the trade will automatically close to
            limit losses.
        takeProfitRate:
          type: number
          format: float
          description: >-
            The take-profit rate at which the trade will automatically close to
            secure profits.
        isTslEnabled:
          type: boolean
          description: Indicates whether a trailing stop-loss is enabled.
        isDiscounted:
          type: boolean
          description: Indicates if the order is eligible for a discount.
        mirrorId:
          type: integer
          description: ID related to mirrored trades, if applicable.
        frozenAmount:
          type: number
          format: float
          description: Amount frozen for the order.
        totalExternalCosts:
          type: number
          format: float
          description: Total external costs associated with the trade.
        isNoTakeProfit:
          type: boolean
          description: True if no take-profit is set for this order.
        isNoStopLoss:
          type: boolean
          description: True if no stop-loss is set for this order.
        lotCount:
          type: number
          format: float
          description: The number of lots in the order.
        openPositionActionType:
          type: integer
          description: Position open reason.
        externalOperation:
          type: object
          description: External operation details, if any.
          nullable: true
    OrderForClose:
      type: object
      properties:
        orderId:
          type: integer
          description: Unique identifier for the closing order.
        orderType:
          type: integer
          description: Type of order executed.
        statusId:
          type: integer
          description: Status of the closing order.
        cid:
          type: integer
          description: Customer ID associated with the order.
        openDateTime:
          type: string
          format: date-time
          description: The timestamp when the order was placed.
        lastUpdate:
          type: string
          format: date-time
          description: The timestamp of the last update to this order.
        instrumentId:
          type: integer
          description: The ID of the instrument traded.
        unitsToDeduct:
          type: number
          format: float
          description: The number of units closed in this order.
        lotsToDeduct:
          type: number
          format: float
          description: The number of lots closed in this order.
        positionId:
          type: integer
          description: The ID of the closed position.
    OrderForCloseMultiple:
      type: object
      properties:
        orderId:
          type: integer
          description: Unique identifier for the closing order.
        orderType:
          type: integer
          description: Type of order executed.
        statusId:
          type: integer
          description: Status of the closing order.
        cid:
          type: integer
          description: Customer ID associated with the order.
        openDateTime:
          type: string
          format: date-time
          description: The timestamp when the order was placed.
        lastUpdate:
          type: string
          format: date-time
          description: The timestamp of the last update to this order.
        instrumentId:
          type: integer
          description: The ID of the instrument traded.
        unitsToDeduct:
          type: number
          format: float
          description: The number of units closed in this order.
        lotsToDeduct:
          type: number
          format: float
          description: The number of lots closed in this order.
        pendingClosePositionIds:
          type: array
          items:
            type: integer
          description: IDs of positions pending close in this order.
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