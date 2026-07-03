> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get aggregated portfolio snapshot

> **Rate limit:** 60 requests per 60 seconds. This is a **dedicated** limit for this endpoint — it is **not shared** with (pooled across) any other endpoint, so the full rate is available to this endpoint alone.

---

Returns a complete snapshot of the authenticated user's investment portfolio, organized by asset. The response includes account-level balances and equity, individually held positions grouped by asset, and any copy-trading relationships the user has active. Use the instrumentIds filter to scope results to a specific set of assets, or mirrorIds to isolate specific copy-trading relationships. Account totals always reflect the full portfolio regardless of filters applied.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/trading/info/aggregate-portfolio
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
  /api/v1/trading/info/aggregate-portfolio:
    get:
      tags:
        - Trading Real
      summary: Get aggregated portfolio snapshot
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is a **dedicated**
        limit for this endpoint — it is **not shared** with (pooled across) any
        other endpoint, so the full rate is available to this endpoint alone.


        ---


        Returns a complete snapshot of the authenticated user's investment
        portfolio, organized by asset. The response includes account-level
        balances and equity, individually held positions grouped by asset, and
        any copy-trading relationships the user has active. Use the
        instrumentIds filter to scope results to a specific set of assets, or
        mirrorIds to isolate specific copy-trading relationships. Account totals
        always reflect the full portfolio regardless of filters applied.
      operationId: getAggregatedPortfolio
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 530eeace-5712-4a75-b429-128540c6c6df
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
        - name: conversionMode
          in: query
          required: false
          schema:
            type: string
            enum:
              - eToroApp
              - Realtime
            default: eToroApp
          description: >-
            Determines which conversion to use for non-USD assets when the
            market is closed. 'Realtime' uses the realtime conversion rate.
            'eToroApp' uses the last conversion rate at market close time.
            Default is 'eToroApp'.
        - name: instrumentIds
          in: query
          required: false
          style: form
          explode: false
          schema:
            type: array
            items:
              type: integer
              format: int32
          description: >-
            Scope the response to a specific list of assets by their eToro
            instrument ID. When omitted, all held assets are returned. Does not
            affect account-level totals.
        - name: mirrorIds
          in: query
          required: false
          style: form
          explode: false
          schema:
            type: array
            items:
              type: integer
              format: int32
          description: >-
            Scope copy-trading data to specific relationships by their mirror
            ID. A mirrorId of 0 refers to positions held directly (not via copy
            trading). When omitted, all copy-trading relationships are included.
      responses:
        '200':
          description: Successfully retrieved aggregated portfolio data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AggregatedPortfolioResponse'
              example:
                cid: 4498
                timestamp: '2026-05-26T15:24:25.267Z'
                accountCurrency: USD
                accountTotals:
                  accountAvailableCash: 4320.84
                  accountFrozenCash: 0
                  accountCurrentPnl: -300.35
                  accountTotalValue: 5154.48
                  accountTotalUsedMargin: 1133.99
                  accountBalance: 4320.84
                instrumentAggregates:
                  - instrumentId: 100000
                    assetCurrency: USD
                    totalMarginAccountCurrency: 849.86
                    totalFees: 0
                    totalFeesAcctCcy: 0
                    totalTaxes: 0
                    totalTaxesAcctCcy: 0
                    totalMarginAssetCurrency: 849.86
                    pnlAssetCurrency: -225.3
                    accountCurrencyRoePercent: -26.51
                    netContracts: 0.008076
                    netUnits: 0.008076
                    netCurrentExposureAssetCurrency: 624.57
                    netCurrentExposureAccountCurrency: 624.57
                    netInitialExposureAccountCurrency: 849.87
                    accountCurrencyReturn: -225.3
                    liquidationValueAccountCurrency: 624.56
                    liquidationValueAssetCurrency: 624.56
                    avgLeverage: 1
                    avgOpenRate: 105233.5041183754
                    netAvgOpenRate: 105233.5041183754
                    avgConversionRate: 1
                mirrors:
                  - mirrorId: 1869651
                    mirrorAvailableCash: 0.04
                    mirrorDepositTotal: 290
                    mirrorWithdrawalTotal: 0
                    mirrorStopLossPercentage: 5
                    mirrorStopLoss: 14.5
                    mirrorClosedPositionsPnl: -0.26
                    mirrorTotals:
                      mirrorNetFunding: 290
                      mirrorPositionsPnl: -75.05
                      mirrorLiquidationValue: 209.08
                      mirrorPositionsPnlPercent: -0.35
                      mirrorMarginPercent: 25.06
                      mirrorValuePercent: 4.06
                      mirrorActiveMargin: 284.13
                    instrumentAggregates: []
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
          description: Invalid request parameters
        '404':
          description: User not found
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
    AggregatedPortfolioResponse:
      type: object
      description: >-
        Complete snapshot of the authenticated user's investment portfolio,
        organized by asset.
      properties:
        cid:
          type: integer
          format: int32
          description: Customer ID.
        timestamp:
          type: string
          format: date-time
          description: Time at which this portfolio snapshot was calculated.
        accountCurrency:
          type: string
          description: ISO 4217 code of the account's base currency (e.g. 'USD').
        accountTotals:
          $ref: '#/components/schemas/AggregatedPortfolioAccountTotals'
        instrumentAggregates:
          type: array
          description: >-
            Positions held directly (not via copy trading), grouped by
            instrument.
          items:
            $ref: '#/components/schemas/AggregatedPortfolioInstrumentAggregate'
        mirrors:
          type: array
          description: Copy-trading relationships the user has active.
          items:
            $ref: '#/components/schemas/AggregatedPortfolioMirrorAggregate'
    AggregatedPortfolioAccountTotals:
      type: object
      description: Account-level balance and equity totals.
      properties:
        accountAvailableCash:
          type: number
          format: double
          description: >-
            Cash available for new trades: accountBalance minus
            accountFrozenCash.
        accountFrozenCash:
          type: number
          format: double
          description: Cash reserved for pending open orders.
        accountCurrentPnl:
          type: number
          format: double
          description: >-
            Unrealized P&L across all manual positions and copy-trading mirrors
            in account currency.
        accountTotalValue:
          type: number
          format: double
          description: >-
            Total portfolio value: accountAvailableCash + accountTotalUsedMargin
            + accountCurrentPnl.
        accountTotalUsedMargin:
          type: number
          format: double
          description: >-
            Total margin in use: manual position margins + frozen order amounts
            + mirror active margins.
        accountBalance:
          type: number
          format: double
          description: Total cash balance (available + frozen), excluding invested amounts.
    AggregatedPortfolioInstrumentAggregate:
      type: object
      description: Aggregated data across all positions for a single instrument.
      properties:
        instrumentId:
          type: integer
          format: int32
          description: eToro instrument identifier.
        assetCurrency:
          type: string
          description: ISO 4217 code of the instrument's base currency (e.g. 'USD', 'EUR').
        totalMarginAccountCurrency:
          type: number
          format: double
          description: >-
            Sum of margins across all positions for this instrument, in account
            currency.
        totalFees:
          type: number
          format: double
          description: >-
            Sum of transaction fees taken on positions of this instrument, in
            asset currency.
        totalFeesAcctCcy:
          type: number
          format: double
          description: >-
            Sum of transaction fees taken on positions of this instrument, in
            account currency.
        totalTaxes:
          type: number
          format: double
          description: Sum of taxes for this instrument, in asset currency.
        totalTaxesAcctCcy:
          type: number
          format: double
          description: Sum of taxes for this instrument, in account currency.
        totalMarginAssetCurrency:
          type: number
          format: double
          description: >-
            Sum of margins across all positions for this instrument, in asset
            currency.
        pnlAssetCurrency:
          type: number
          format: double
          nullable: true
          description: >-
            Unrealized P&L for this instrument in asset currency. Null when P&L
            calculation is not requested.
        accountCurrencyRoePercent:
          type: number
          format: double
          description: >-
            Return on equity in account currency: accountCurrencyReturn /
            totalMarginAccountCurrency.
        netContracts:
          type: number
          format: double
          description: >-
            Net contracts across all positions (positive = net long, negative =
            net short).
        netUnits:
          type: number
          format: double
          description: >-
            Net units across all positions (positive = net long, negative = net
            short).
        netCurrentExposureAssetCurrency:
          type: number
          format: double
          description: Net current market exposure in asset currency.
        netCurrentExposureAccountCurrency:
          type: number
          format: double
          description: Net current market exposure in account currency.
        netInitialExposureAccountCurrency:
          type: number
          format: double
          description: Net initial exposure at open in account currency.
        accountCurrencyReturn:
          type: number
          format: double
          description: Unrealized P&L for this instrument in account currency.
        liquidationValueAccountCurrency:
          type: number
          format: double
          description: >-
            Current liquidation value in account currency:
            totalMarginAccountCurrency + accountCurrencyReturn.
        liquidationValueAssetCurrency:
          type: number
          format: double
          description: Current liquidation value in asset currency.
        avgLeverage:
          type: number
          format: double
          description: Average leverage across all positions for this instrument.
        avgOpenRate:
          type: number
          format: double
          description: Weighted average open rate across all positions for this instrument.
        netAvgOpenRate:
          type: number
          format: double
          description: >-
            Direction-aware weighted average open rate (long contributions minus
            short).
        avgConversionRate:
          type: number
          format: double
          description: >-
            Weighted average asset-to-account-currency conversion rate at
            position open.
    AggregatedPortfolioMirrorAggregate:
      type: object
      description: Aggregated data for a single copy-trading relationship.
      properties:
        mirrorId:
          type: integer
          format: int32
          description: Mirror identifier. A value of 0 represents manually held positions.
        mirrorAvailableCash:
          type: number
          format: double
          description: Cash available within this mirror for new copy positions.
        mirrorDepositTotal:
          type: number
          format: double
          description: >-
            Total amount ever deposited into this mirror: initialInvestment +
            depositSummary.
        mirrorWithdrawalTotal:
          type: number
          format: double
          description: Total amount ever withdrawn from this mirror.
        mirrorStopLossPercentage:
          type: number
          format: double
          description: Stop-loss threshold as a percentage of the mirror's current value.
        mirrorStopLoss:
          type: number
          format: double
          description: >-
            Stop-loss threshold in account currency. The mirror liquidates when
            its value falls to this level.
        mirrorClosedPositionsPnl:
          type: number
          format: double
          description: Accumulated net profit from all closed positions within this mirror.
        mirrorTotals:
          $ref: '#/components/schemas/AggregatedPortfolioMirrorTotals'
        instrumentAggregates:
          type: array
          description: >-
            Positions held within this copy-trading mirror, grouped by
            instrument.
          items:
            $ref: '#/components/schemas/AggregatedPortfolioInstrumentAggregate'
    AggregatedPortfolioMirrorTotals:
      type: object
      description: Aggregated totals for a copy-trading mirror.
      properties:
        mirrorNetFunding:
          type: number
          format: double
          description: >-
            Net amount funded into the mirror: mirrorDepositTotal minus
            mirrorWithdrawalTotal.
        mirrorPositionsPnl:
          type: number
          format: double
          description: >-
            Total P&L from open and closed positions within the mirror, in
            account currency.
        mirrorLiquidationValue:
          type: number
          format: double
          description: 'Current mirror value: mirrorActiveMargin + mirrorPositionsPnl.'
        mirrorPositionsPnlPercent:
          type: number
          format: double
          description: mirrorPositionsPnl as a percentage of mirrorLiquidationValue.
        mirrorMarginPercent:
          type: number
          format: double
          description: >-
            This mirror's active margin as a percentage of the account's total
            used margin.
        mirrorValuePercent:
          type: number
          format: double
          description: >-
            This mirror's liquidation value as a percentage of the account's
            total value.
        mirrorActiveMargin:
          type: number
          format: double
          description: >-
            Total margin in active use within this mirror: mirrorAvailableCash +
            sum of position margins minus closed positions P&L.
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