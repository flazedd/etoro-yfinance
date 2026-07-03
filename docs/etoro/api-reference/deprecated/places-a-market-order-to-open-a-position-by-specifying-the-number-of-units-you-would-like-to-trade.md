> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Places a Market Order to open a position by specifying the number of units you would like to trade.

> Deprecated: This endpoint is no longer present in the current eToro Public API Swagger. Prefer the current replacement endpoints where available.

This endpoint allows traders to place a market order to open a position by specifying the number of units (rather than an amount in cash). The trade is executed at the current market price, and optional settings like leverage, stop-loss, and take-profit can be applied.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/trading/execution/demo/market-open-orders/by-units
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
  /api/v1/trading/execution/demo/market-open-orders/by-units:
    post:
      tags:
        - Deprecated
      summary: >-
        Places a Market Order to open a position by specifying the number of
        units you would like to trade.
      description: >-
        Deprecated: This endpoint is no longer present in the current eToro
        Public API Swagger. Prefer the current replacement endpoints where
        available.


        This endpoint allows traders to place a market order to open a position
        by specifying the number of units (rather than an amount in cash). The
        trade is executed at the current market price, and optional settings
        like leverage, stop-loss, and take-profit can be applied.
      operationId: openMarketPositionByUnitsDemo
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: f4ce3033-f7d7-426d-96b4-f261ef64c05e
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
        content:
          application/json:
            schema:
              type: object
              properties:
                InstrumentID:
                  type: integer
                  format: int32
                  description: The unique identifier of the financial instrument to trade.
                IsBuy:
                  type: boolean
                  description: True for a long position, false for a short position.
                Leverage:
                  type: integer
                  format: int32
                  description: The leverage multiplier for the trade.
                AmountInUnits:
                  type: number
                  format: double
                  description: >-
                    The number of units of the asset. Required if Amount is not
                    provided. For most assets this can be a fractional number.
                    Note that for Future Contracts this number should indicate
                    the number of underlying units, and not the number of
                    contracts, according to the formula: AmountInUnits =
                    contract multiplier * number of contracts.
                StopLossRate:
                  type: number
                  format: double
                  nullable: true
                  description: >-
                    The stop-loss trigger price at which the position will
                    generate a Market Order to close (after it was opened).
                    StopLoss trigger price must be worse than current price.
                TakeProfitRate:
                  type: number
                  format: double
                  nullable: true
                  description: >-
                    The take-profit trigger price at which the position will
                    generate a Market Order to close (after it has opened).
                    TakeProfit trigger price must be better than the current
                    price.
                IsTslEnabled:
                  type: boolean
                  nullable: true
                  description: >-
                    Indicates if a trailing stop loss (TSL) is enabled. This
                    means that the stoploss rate indicated will get updated
                    automatically whenever the asset price increases (for long
                    positions) or decreases (for short position) effectively
                    keeping the stoploss in a constant gap from the best price
                    achieved so far.
                IsNoStopLoss:
                  type: boolean
                  nullable: true
                  description: True if no stop-loss is set for this order.
                IsNoTakeProfit:
                  type: boolean
                  nullable: true
                  description: True if no take-profit is set for this order.
              required:
                - InstrumentID
                - IsBuy
                - Leverage
                - AmountInUnits
      responses:
        '200':
          description: Successfully opened a market order.
          content:
            application/json:
              schema:
                type: object
                properties:
                  orderForOpen:
                    type: object
                    properties:
                      instrumentID:
                        type: integer
                        description: The ID of the traded instrument.
                      amount:
                        type: integer
                        description: The amount invested in the trade.
                      amountInUnits:
                        type: number
                        format: double
                        description: The number of units traded.
                      isBuy:
                        type: boolean
                        description: True for a long position, false for a short position.
                      leverage:
                        type: integer
                        description: The leverage applied to the trade.
                      stopLossRate:
                        type: integer
                        description: The stop-loss threshold rate, if applicable.
                      takeProfitRate:
                        type: integer
                        description: The take-profit thereshold rate, if applicable.
                      isTslEnabled:
                        type: boolean
                        description: Indicates if trailing stop-loss is enabled.
                      mirrorID:
                        type: integer
                        description: ID related to mirrored trades, if applicable.
                      totalExternalCosts:
                        type: integer
                        description: Total external costs associated with the trade.
                      lotCount:
                        type: integer
                        description: The number of lots in the order.
                      orderID:
                        type: integer
                        description: The unique order identifier.
                      orderType:
                        type: integer
                        description: The type of order executed.
                      statusID:
                        type: integer
                        description: The status of the order.
                      CID:
                        type: integer
                        description: Customer Account ID associated with the order.
                      openDateTime:
                        type: string
                        format: date-time
                        description: The timestamp when the order was opened.
                      lastUpdate:
                        type: string
                        format: date-time
                        description: The last update timestamp of the order.
                  token:
                    type: string
                    format: uuid
                    description: A unique confirmation token for the order.
              example:
                orderForOpen:
                  instrumentID: 100000
                  amount: 0
                  amountInUnits: 0.001
                  isBuy: true
                  leverage: 1
                  stopLossRate: 0
                  takeProfitRate: 0
                  isTslEnabled: false
                  mirrorID: 0
                  totalExternalCosts: 0
                  lotCount: 0
                  orderID: 13906629
                  orderType: 18
                  statusID: 1
                  CID: 7765437
                  openDateTime: '2025-04-02T15:56:50.7496838Z'
                  lastUpdate: '2025-04-02T15:56:50.7496838Z'
                token: 43ceb769-cff6-45ec-8ad7-292b7401353f
      deprecated: true

````