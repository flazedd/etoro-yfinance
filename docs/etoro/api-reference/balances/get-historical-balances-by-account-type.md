> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get historical balances by account type

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Returns end-of-day balance snapshots for a specific account type for the authenticated user. History is available for the last 12 months. The maximum date range per request is 365 days.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/balances/{accountType}/history
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
  /api/v1/balances/{accountType}/history:
    get:
      tags:
        - Balances
      summary: Get historical balances by account type
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Returns end-of-day balance snapshots for a specific account type for the
        authenticated user. History is available for the last 12 months. The
        maximum date range per request is 365 days.
      operationId: getHistoricalBalancesByAccountType
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 4b40a4d9-2acb-420e-923c-0e43d24678d4
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
        - name: accountType
          in: path
          required: true
          description: The account type to retrieve historical balances for.
          schema:
            $ref: '#/components/schemas/BalanceAggregatorApi_AccountType'
        - name: displayCurrency
          in: query
          description: ISO 4217 currency code for totals and conversions. Defaults to USD.
          schema:
            type: string
            default: USD
        - name: fromDate
          in: query
          description: >-
            Start of the date range (inclusive). Format: YYYY-MM-DD (ISO 8601).
            Defaults to toDate minus 30 days. Must be within the last 12 months.
            Maximum range with toDate: 365 days.
          schema:
            type: string
            format: date
        - name: toDate
          in: query
          description: >-
            End of the date range (inclusive). Format: YYYY-MM-DD (ISO 8601).
            Defaults to today (UTC). Maximum range with fromDate: 365 days.
          schema:
            type: string
            format: date
        - name: accountIds
          in: query
          description: Optional comma-separated list of account IDs to include.
          schema:
            type: string
      responses:
        '200':
          description: >-
            Historical balance snapshots for the specified account type
            retrieved successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetHistoricalBalancesResponse'
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
          description: >-
            Bad Request — invalid account type, date range, or query parameter
            value.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BalancesErrorResponse'
        '401':
          description: Unauthorized — missing or invalid authentication credentials.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BalanceAggregatorApi_PublicErrorResponse'
              example:
                errorCode: Unauthorized
                errorMessage: Unauthorized
        '403':
          description: >-
            Forbidden — the token does not include the
            etoro-public:money.balance:read scope.
        '404':
          description: >-
            Not Found — no historical data found for the specified account type
            and date range.
        '429':
          description: Too Many Requests — rate limit exceeded.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BalanceAggregatorApi_PublicErrorResponse'
              example:
                errorCode: TooManyRequests
                errorMessage: Too many requests
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
        '500':
          description: Internal Server Error.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BalanceAggregatorApi_PublicErrorResponse'
              example:
                errorCode: UnhandledException
                errorMessage: Global Error
      security:
        - oauth2:
            - etoro-public:money.balance:read
components:
  schemas:
    BalanceAggregatorApi_AccountType:
      type: string
      description: The type of eToro account.
      enum:
        - Trading
        - Cash
        - Options
        - Crypto
        - MoneyFarm
        - Spaceship
    GetHistoricalBalancesResponse:
      type: object
      description: Historical end-of-day balance snapshots for the authenticated user.
      properties:
        gcid:
          type: integer
          format: int64
          description: The user's global customer ID.
        displayCurrency:
          type: string
          nullable: true
          description: ISO 4217 currency code used for display values.
        fromDate:
          type: string
          format: date
          description: Start of the returned date range (inclusive, ISO 8601).
        toDate:
          type: string
          format: date
          description: End of the returned date range (inclusive, ISO 8601).
        snapshots:
          type: array
          items:
            $ref: '#/components/schemas/HistoricalDailySnapshotData'
          nullable: true
          description: >-
            End-of-day balance snapshots, one entry per day in the requested
            range.
      additionalProperties: false
    BalancesErrorResponse:
      type: object
      description: Error response returned for client-side errors (4xx).
      properties:
        code:
          type: string
          nullable: true
          description: Error code (e.g., VALIDATION_ERROR, USER_NOT_FOUND).
        message:
          type: string
          nullable: true
          description: Human-readable error message.
        requestId:
          type: string
          nullable: true
          description: Request ID for tracing and support.
      additionalProperties: false
    BalanceAggregatorApi_PublicErrorResponse:
      type: object
      description: Standard error response returned by the API gateway.
      properties:
        errorCode:
          type: string
          nullable: true
          description: Error code.
        errorMessage:
          type: string
          nullable: true
          description: Human-readable error message.
      additionalProperties: false
    HistoricalDailySnapshotData:
      type: object
      description: End-of-day balance snapshot for a specific date.
      properties:
        date:
          type: string
          format: date
          description: The snapshot date (ISO 8601).
        totalCurrencyIso:
          type: string
          nullable: true
          description: ISO 4217 currency code for the total figures in native currency.
        totalCash:
          type: number
          format: double
          description: Total cash across all accounts in native currency.
        totalInvestedAmount:
          type: number
          format: double
          description: Total invested amount across all accounts in native currency.
        totalPnl:
          type: number
          format: double
          description: Total profit and loss across all accounts in native currency.
        totalBalance:
          type: number
          format: double
          description: Total balance across all accounts in native currency.
        displayTotalCash:
          type: number
          format: double
          description: Total cash converted to the requested display currency.
        displayTotalInvestedAmount:
          type: number
          format: double
          description: Total invested amount converted to the requested display currency.
        displayTotalPnl:
          type: number
          format: double
          description: Total profit and loss converted to the requested display currency.
        displayTotalBalance:
          type: number
          format: double
          description: Total balance converted to the requested display currency.
        totalExchangeRate:
          type: number
          format: double
          description: Exchange rate applied to convert totals to displayCurrency.
        accountSnapshots:
          type: array
          items:
            $ref: '#/components/schemas/HistoricalAccountData'
          nullable: true
          description: Individual account breakdowns within this snapshot.
      additionalProperties: false
    HistoricalAccountData:
      type: object
      description: Individual account balance within a historical daily snapshot.
      properties:
        accountId:
          type: string
          nullable: true
          description: Unique identifier of the account.
        accountType:
          $ref: '#/components/schemas/BalanceAggregatorApi_AccountType'
        currency:
          type: string
          nullable: true
          description: The account's native currency (ISO 4217).
        cash:
          type: number
          format: double
          description: Cash balance in the account's native currency.
        investedAmount:
          type: number
          format: double
          description: Invested amount in the account's native currency.
        pnl:
          type: number
          format: double
          description: Profit and loss in the account's native currency.
        total:
          type: number
          format: double
          description: Total balance in the account's native currency.
        usdRate:
          type: number
          format: double
          description: Exchange rate to USD.
        displayCash:
          type: number
          format: double
          description: Cash balance converted to the requested display currency.
        displayInvestedAmount:
          type: number
          format: double
          description: Invested amount converted to the requested display currency.
        displayPnl:
          type: number
          format: double
          description: Profit and loss converted to the requested display currency.
        displayTotal:
          type: number
          format: double
          description: Total balance converted to the requested display currency.
        exchangeRate:
          type: number
          format: double
          description: Exchange rate applied to convert to displayCurrency.
      additionalProperties: false
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