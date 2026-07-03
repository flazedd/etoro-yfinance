> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Check trading permissions, limits, and available leverage for one or more instruments

> Deprecated: This endpoint is no longer present in the current eToro Public API Swagger. Prefer the current replacement endpoints where available.

Returns per-instrument trading configuration for the authenticated account - position limits, permitted order types, stop-loss and take-profit boundaries, and available leverage by settlement type and direction. Instruments not found are listed in notFoundInstrumentIds and notFoundSymbols. At least one of instrumentIds or symbols must be supplied; the combined length must not exceed 100 instruments.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/trading/info/demo/eligibility
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
  /api/v1/trading/info/demo/eligibility:
    post:
      tags:
        - Deprecated
      summary: >-
        Check trading permissions, limits, and available leverage for one or
        more instruments
      description: >-
        Deprecated: This endpoint is no longer present in the current eToro
        Public API Swagger. Prefer the current replacement endpoints where
        available.


        Returns per-instrument trading configuration for the authenticated
        account - position limits, permitted order types, stop-loss and
        take-profit boundaries, and available leverage by settlement type and
        direction. Instruments not found are listed in notFoundInstrumentIds and
        notFoundSymbols. At least one of instrumentIds or symbols must be
        supplied; the combined length must not exceed 100 instruments.
      operationId: getInstrumentEligibilityDemoDeprecated
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 21e80d1f-5f99-4f93-b337-5f5e63582279
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
              $ref: '#/components/schemas/InstrumentEligibilityRequest'
            example:
              instrumentIds:
                - 1001
              symbols:
                - AAPL
              currency: USD
      responses:
        '200':
          description: Eligibility resolved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InstrumentEligibilityResponse'
              example:
                currency: USD
                eligibilities:
                  - instrumentId: 1001
                    symbol: AAPL
                    minPositionExposure: 50
                    maxUnitsPerOrder: 10000
                    allowOpenPosition: true
                    allowClosePosition: true
                    allowPartialClosePosition: true
                    allowMitOrders: true
                    allowEntryOrders: false
                    allowExitOrders: false
                    allowTrailingStopLoss: true
                    requiresW8Ben: null
                    unitsQuantityType: FractionalUnits
                    orderFillBehaviorType: BestEffort
                    allowedOrderQuantityType: Both
                    tradeUnitType: Units
                    initialMarginInAssetCurrency: null
                    stopLossMarginInAssetCurrency: null
                    additionalBufferPercent: null
                    leverageConfigs:
                      - settlementType: CFD
                        direction: LONG
                        leverageValues:
                          - 1
                          - 2
                          - 5
                        isPotential: false
                        minPositionAmount: 50
                        allowEditStopLoss: true
                        minStopLossPercentage: 5
                        maxStopLossPercentage: 50
                        defaultStopLossPercentage: 50
                        allowEditTakeProfit: true
                        minTakeProfitPercentage: 5
                        maxTakeProfitPercentage: 1000
                        defaultTakeProfitPercentage: 1000
                        allowStopLossTakeProfit: true
                notFoundInstrumentIds: []
                notFoundSymbols: []
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
        '500':
          description: Internal server error.
      deprecated: true
      security:
        - bearerAuth: []
components:
  schemas:
    InstrumentEligibilityRequest:
      type: object
      description: >-
        Request payload for checking instrument eligibility. At least one of
        `instrumentIds` or `symbols` must be provided; combined length must not
        exceed 100 instruments.
      properties:
        instrumentIds:
          type: array
          items:
            type: integer
            format: int32
          nullable: true
          description: Optional list of instrument IDs to check.
        symbols:
          type: array
          items:
            type: string
          nullable: true
          description: Optional list of instrument symbols to check.
        currency:
          type: string
          default: USD
          description: >-
            Requested currency for financial amounts in the eligibility response
            (e.g. minimum position size). Currently only USD is supported.
    InstrumentEligibilityResponse:
      type: object
      description: Response containing trading configuration for all requested instruments.
      properties:
        currency:
          type: string
          description: The currency used for all monetary values in this response.
        eligibilities:
          type: array
          items:
            $ref: '#/components/schemas/InstrumentEligibility'
          description: Trading configuration for each resolved instrument.
        notFoundInstrumentIds:
          type: array
          items:
            type: integer
            format: int32
          description: Instrument IDs that were requested but could not be found.
        notFoundSymbols:
          type: array
          items:
            type: string
          description: Symbols that were requested but could not be found.
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
    InstrumentEligibility:
      type: object
      description: >-
        Full trading configuration for a single instrument, including position
        limits, trading permissions, order configuration, margin settings, and
        available leverage.
      properties:
        instrumentId:
          type: integer
          format: int32
          description: Unique identifier for the instrument.
        symbol:
          type: string
          description: Trading symbol of the instrument (e.g. AAPL, EURUSD).
        minPositionExposure:
          type: number
          format: decimal
          description: >-
            Minimum exposure value required to open a position on this
            instrument.
        maxUnitsPerOrder:
          type: number
          format: decimal
          description: Maximum number of units allowed per single order.
        allowOpenPosition:
          type: boolean
          description: Whether opening new positions is currently permitted.
        allowClosePosition:
          type: boolean
          description: Whether closing existing positions is currently permitted.
        allowPartialClosePosition:
          type: boolean
          description: Whether partially closing an existing position is permitted.
        allowMitOrders:
          type: boolean
          description: Whether Market-if-Touched (limit) orders are supported.
        allowEntryOrders:
          type: boolean
          description: Whether submitting open orders when the market is closed is allowed.
        allowExitOrders:
          type: boolean
          description: >-
            Whether submitting close orders when the market is closed is
            allowed.
        allowTrailingStopLoss:
          type: boolean
          description: >-
            Whether a trailing stop-loss can be set on positions for this
            instrument.
        requiresW8Ben:
          type: boolean
          nullable: true
          description: >-
            Whether a W-8BEN tax form is required to trade this instrument. Null
            if not applicable.
        unitsQuantityType:
          type: string
          description: >-
            What trade quantity type is allowed. Possible values: `whole`,
            `fractional`.
        orderFillBehaviorType:
          type: string
          description: >-
            How orders are filled for this instrument. Possible values:
            `bestEffort`, `fillOrKill`.
        allowedOrderQuantityType:
          type: string
          description: >-
            Which order sizing methods the instrument allows. Possible values:
            `unitsOnly`, `amountOnly`, `all`.
        tradeUnitType:
          type: string
          description: >-
            Unit type used to express trade size. Possible values: `units`,
            `lots`.
        initialMarginInAssetCurrency:
          type: number
          format: decimal
          nullable: true
          description: >-
            Initial margin expressed in the asset currency. Null if not
            applicable.
        stopLossMarginInAssetCurrency:
          type: number
          format: decimal
          nullable: true
          description: >-
            Stop-loss margin expressed in the asset currency. Null if not
            applicable.
        additionalBufferPercent:
          type: number
          format: decimal
          nullable: true
          description: >-
            Additional buffer applied to the current rate to limit the order
            execution price - usually for low-liquidity assets. This also causes
            additional funds to be reserved for the order. Null if no buffer.
        leverageConfigs:
          type: array
          items:
            $ref: '#/components/schemas/LeverageConfiguration'
          description: >-
            Available leverage configurations, each specific to a settlement
            type and direction.
    LeverageConfiguration:
      type: object
      description: >-
        Leverage configuration for a specific settlement type and trade
        direction combination.
      properties:
        settlementType:
          type: string
          description: >-
            The settlement type this configuration applies to. Possible values:
            `cfd`, `real`, `realFutures`, `marginTrade`.
        direction:
          type: string
          description: 'The trade direction. Possible values: `long`, `short`.'
        leverageValues:
          type: array
          items:
            type: integer
            format: int32
          description: >-
            Available leverage multipliers for this settlement type and
            direction.
        isPotential:
          type: boolean
          description: >-
            Additional user questionnaire may be required to allow the user to
            trade with this setup of settlement and leverages.
        minPositionAmount:
          type: number
          format: decimal
          description: >-
            Minimum monetary collateral required to open a position under this
            leverage configuration.
        allowEditStopLoss:
          type: boolean
          description: >-
            Whether the stop-loss can be edited for positions under this
            configuration.
        minStopLossPercentage:
          type: number
          format: decimal
          description: >-
            Minimum stop-loss percentage allowed from the allocated margin of
            the position.
        maxStopLossPercentage:
          type: number
          format: decimal
          description: >-
            Maximum stop-loss percentage allowed from the allocated margin of
            the position.
        defaultStopLossPercentage:
          type: number
          format: decimal
          description: >-
            Default stop-loss percentage applied when no explicit value is
            provided.
        allowEditTakeProfit:
          type: boolean
          description: Whether the take-profit can be edited.
        minTakeProfitPercentage:
          type: number
          format: decimal
          description: >-
            Minimum take-profit percentage allowed from the allocated margin of
            the position.
        maxTakeProfitPercentage:
          type: number
          format: decimal
          description: >-
            Maximum take-profit percentage allowed from the allocated margin of
            the position.
        defaultTakeProfitPercentage:
          type: number
          format: decimal
          description: >-
            Default take-profit percentage applied when no explicit value is
            provided.
        allowStopLossTakeProfit:
          type: boolean
          description: Whether stop-loss and take-profit can be set on a position.

````