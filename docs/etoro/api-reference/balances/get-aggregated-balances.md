> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get aggregated balances

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Returns aggregated balances across all account types for the authenticated user. Optionally filter by account type or specify the display currency for totals.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/balances
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
  /api/v1/balances:
    get:
      tags:
        - Balances
      summary: Get aggregated balances
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Returns aggregated balances across all account types for the
        authenticated user. Optionally filter by account type or specify the
        display currency for totals.
      operationId: getBalances
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 61765e32-944d-4387-8f08-0ecad697d978
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
        - name: accountTypes
          in: query
          description: >-
            Optional comma-separated list of account types to include. Valid
            values: Trading, Cash, Options, Crypto, MoneyFarm, Spaceship.
          schema:
            type: string
        - name: displayCurrency
          in: query
          description: ISO 4217 currency code for totals and conversions. Defaults to USD.
          schema:
            type: string
            default: USD
        - name: includeZeroBalances
          in: query
          description: >-
            Whether to include accounts with a zero balance in the response.
            Defaults to false.
          schema:
            type: boolean
        - name: expand
          in: query
          description: >-
            Comma-separated list of optional sections to include in the
            response. Valid values: equityDetails.
          schema:
            type: string
      responses:
        '200':
          description: Aggregated balances retrieved successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetBalancesResponse'
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
          description: Bad Request — invalid query parameter value.
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
    GetBalancesResponse:
      type: object
      description: Aggregated balances for the authenticated user.
      properties:
        gcid:
          type: integer
          format: int64
          description: The user's global customer ID.
        totalBalance:
          type: number
          format: double
          description: >-
            Sum of all account balances converted to the requested display
            currency.
        displayCurrency:
          type: string
          nullable: true
          description: >-
            ISO 4217 currency code used for totalBalance and displayBalance
            values.
        balances:
          type: array
          items:
            $ref: '#/components/schemas/AccountBalanceData'
          nullable: true
          description: Individual account balances.
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
    AccountBalanceData:
      type: object
      description: Balance data for a single account.
      properties:
        accountId:
          type: string
          nullable: true
          description: Unique identifier of the account.
        accountType:
          $ref: '#/components/schemas/BalanceAggregatorApi_AccountType'
        subType:
          type: string
          nullable: true
          description: Account sub-type, where applicable.
        balance:
          type: number
          format: double
          description: Account balance in the account's native currency.
        currency:
          type: string
          nullable: true
          description: The account's native currency (ISO 4217).
        displayBalance:
          type: number
          format: double
          description: Account balance converted to the requested display currency.
        displayCurrency:
          type: string
          nullable: true
          description: The display currency (ISO 4217) used for displayBalance.
        exchangeRate:
          type: number
          format: double
          description: Exchange rate applied to convert balance to displayCurrency.
        equityDetails:
          $ref: '#/components/schemas/EquityDetailsData'
      additionalProperties: false
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
    EquityDetailsData:
      type: object
      description: >-
        Provider-specific balance details, returned only when the request
        includes expand=equityDetails. All fields are nullable; only fields
        relevant to the account's provider are populated. Trading accounts
        populate available/frozenCash/currentPNL/totalUsedMargin; Crypto
        accounts populate cryptoId, the balance variants,
        fiatConversionCurrency, and orderIndex.
      properties:
        available:
          type: number
          format: double
          nullable: true
          description: >-
            Available balance or buying power (Trading, Options, MoneyFarm,
            Cash).
        frozenCash:
          type: number
          format: double
          nullable: true
          description: Cash frozen by the platform pending settlement (Trading).
        currentPNL:
          type: number
          format: double
          nullable: true
          description: Current unrealized profit and loss on open positions (Trading).
        totalUsedMargin:
          type: number
          format: double
          nullable: true
          description: Total margin used by open positions (Trading).
        cryptoId:
          type: integer
          format: int32
          nullable: true
          description: eToro internal crypto asset identifier (Crypto).
        balance:
          type: number
          format: double
          nullable: true
          description: Balance in native crypto units (Crypto).
        totalBalance:
          type: number
          format: double
          nullable: true
          description: Total balance in native crypto units, including pending (Crypto).
        spendableBalance:
          type: number
          format: double
          nullable: true
          description: Spendable balance in native crypto units (Crypto).
        balanceInFiat:
          type: number
          format: double
          nullable: true
          description: Balance converted to fiat (Crypto).
        totalBalanceInFiat:
          type: number
          format: double
          nullable: true
          description: Total balance converted to fiat, including pending (Crypto).
        spendableBalanceInFiat:
          type: number
          format: double
          nullable: true
          description: Spendable balance converted to fiat (Crypto).
        fiatConversionCurrency:
          type: string
          nullable: true
          description: ISO 4217 currency code used for the InFiat values (Crypto).
        orderIndex:
          type: integer
          format: int32
          nullable: true
          description: Display order index for sorting (Crypto).
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