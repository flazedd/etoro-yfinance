> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get instrument by symbol (shortener)

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Retrieve a single instrument by its trading symbol, restricted to the field set defined by the given shortener preset. The `fields` query parameter can further narrow the projection to a subset of the shortener's fields.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/instruments/{symbol}/{shortener}
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
  /api/v1/instruments/{symbol}/{shortener}:
    get:
      tags:
        - Asset Explorer
      summary: Get instrument by symbol (shortener)
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Retrieve a single instrument by its trading symbol, restricted to the
        field set defined by the given shortener preset. The `fields` query
        parameter can further narrow the projection to a subset of the
        shortener's fields.
      operationId: getInstrumentsBySymbolByShortener
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 650b4819-7896-422e-9f77-f19b39aec2c5
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
        - name: symbol
          in: path
          description: The trading symbol of the instrument (e.g. `AAPL`, `BTC`).
          required: true
          schema:
            type: string
          example: AAPL
        - name: shortener
          in: path
          description: >-
            The name of an allowed shortener preset that restricts the returned
            field set.
          required: true
          schema:
            type: string
          example: summary
        - name: fields
          in: query
          description: >-
            Comma-separated list of `Instrument` fields to include in the
            response. Must be a subset of the shortener's fields. Example:
            `symbol,displayName,currentRate`.
          required: false
          schema:
            type: string
      responses:
        '200':
          description: >-
            Successful response containing the instrument restricted to the
            shortener's fields.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AssetExplorer_Instrument'
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
        '400':
          description: The provided shortener is not in the allowed list.
        '404':
          description: No instrument found for the given symbol.
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
components:
  schemas:
    AssetExplorer_Instrument:
      type: object
      description: >-
        An instrument record. The properties listed below are the only supported
        field names; they may all be used in the `fields`, `sort`, and filter
        (`<field>`, `<field>Min`, `<field>Max`) query parameters. Use the
        `fields` query parameter to project a subset; if `fields` is omitted,
        all properties are returned.
      properties:
        instrumentId:
          type: integer
          format: int32
          description: The unique identifier of the instrument.
        symbol:
          type: string
          description: The full trading symbol of the instrument.
        displayName:
          type: string
          description: The display name of the instrument.
        assetClass:
          type: string
          description: The asset class of the instrument (e.g. Stocks, ETF, Crypto).
        exchangeName:
          type: string
          description: The name of the exchange where the instrument is traded.
        countryCode:
          type: string
          description: The country code of the issuer's corporate location.
        industryName:
          type: string
          description: The industry of the issuer.
        sectorName:
          type: string
          description: The sector of the issuer.
        umbrellaSector:
          type: string
          description: The umbrella sector of the issuer.
        currentRate:
          type: number
          description: The current rate of the instrument.
        marketCap:
          type: number
          description: The market capitalization.
        peRatio:
          type: number
          description: The price-to-earnings ratio.
        beta:
          type: number
          description: The beta of the instrument.
        dividendYieldFiscal:
          type: number
          description: The fiscal dividend yield.
        ceo:
          type: string
          description: The name of the CEO.
        numberOfEmployees:
          type: integer
          format: int64
          description: The number of employees.
        companyFoundedDate:
          type: string
          format: date
          description: The date the company was founded.
        isETFLeveraged:
          type: boolean
          description: Indicates whether the ETF is leveraged.
        etfLeverage:
          type: number
          description: The leverage factor of the ETF.
        netExpenseRatio:
          type: number
          description: The net expense ratio of the ETF.
        prospectusLink:
          type: string
          description: URL to the ETF prospectus document.
        inceptionDate:
          type: string
          format: date
          description: The inception date of the instrument.
        cryptoMarketCap:
          type: number
          description: The market capitalization of the crypto asset.
        cryptoMarketCapRank:
          type: integer
          format: int32
          description: The market capitalization rank of the crypto asset.
        percentOfCryptoMarketCap:
          type: number
          description: The crypto asset's share of total crypto market capitalization.
        cryptoCirculatingSupply:
          type: number
          description: The circulating supply of the crypto asset.
        cryptoMaxSupply:
          type: number
          description: The maximum supply of the crypto asset.
        cryptoTotalSupply:
          type: number
          description: The total supply of the crypto asset.
        cryptoWebsite:
          type: string
          description: The official website URL of the crypto project.
        cryptoWhitePaper:
          type: string
          description: URL to the crypto white paper.
        salesOrRevenue:
          type: number
          description: Sales or revenue (TTM).
        consolidatedNetIncome:
          type: number
          description: Consolidated net income (TTM).
        epsTTM:
          type: number
          description: Earnings per share over the trailing twelve months.
        epsAnnual:
          type: number
          description: Annual earnings per share.
        quarterlyEpsValue:
          type: number
          description: Earnings per share for the most recently reported quarter.
        quarterlySalesValue:
          type: number
          description: Sales for the most recently reported quarter.
        ebitda:
          type: number
          description: >-
            Earnings before interest, taxes, depreciation, and amortization
            (TTM).
        dividendRate:
          type: number
          description: The dividend rate.
        dividendsPerShare:
          type: number
          description: Dividends per share over the last twelve months.
        grossIncomeMargin:
          type: number
          description: The gross income margin (TTM).
        operatingMargin:
          type: number
          description: The operating margin.
        netProfitMargin:
          type: number
          description: The net profit margin.
        fiveYearAverageNetProfitMargin:
          type: number
          description: The 5-year average net profit margin.
        sharesOutstanding:
          type: number
          description: The number of shares outstanding.
        totalEnterpriseValue:
          type: number
          description: The total enterprise value (TTM).
        longTermDebtToEquityRatio:
          type: number
          description: The long-term debt to equity ratio.
        totalDebtToEquityRatio:
          type: number
          description: The total debt to equity ratio (TTM).
        quickRatio:
          type: number
          description: The quick ratio (TTM).
        currentRatio:
          type: number
          description: The current ratio (TTM).
        netOperatingCashFlow:
          type: number
          description: Net operating cash flow (TTM).
        cashFlowPerShare:
          type: number
          description: Cash flow per share.
        cashFlowFromOperPerShareNet:
          type: number
          description: Net cash flow from operations per share (TTM).
        revenuePerShare:
          type: number
          description: Revenue per share (TTM).
        oneYearAnnualRevenueGrowthRate:
          type: number
          description: The 1-year annual revenue growth rate.
        fiveYearAverageReturnOnInvestedCapital:
          type: number
          description: The 5-year average return on invested capital.
        enterpriseValueToEbitda:
          type: number
          description: The enterprise value to EBITDA ratio.
        enterpriseValueToSales:
          type: number
          description: The enterprise value to sales ratio.
        enterpriseValueToOperCashFlow:
          type: number
          description: The enterprise value to operating cash flow ratio.
        nextEarningDate:
          type: string
          format: date
          description: The next earnings release date.
        nextEarningsDateQuarter:
          type: string
          description: The fiscal quarter of the next earnings release.
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