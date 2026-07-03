> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# List cash account transactions (paginated)

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Returns a cursor-paginated list of transactions for the given cash account. Use pageSize and pageToken for pagination; nextPageToken is null when there is no next page.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/money/accounts/cash/{accountId}/transactions
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
  /api/v1/money/accounts/cash/{accountId}/transactions:
    get:
      tags:
        - Cash Accounts
      summary: List cash account transactions (paginated)
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Returns a cursor-paginated list of transactions for the given cash
        account. Use pageSize and pageToken for pagination; nextPageToken is
        null when there is no next page.
      operationId: listCashAccountTransactions
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 1284cb74-f1a5-4021-9760-c34d5fad89e6
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
        - name: accountId
          in: path
          required: true
          schema:
            type: string
            format: uuid
          description: Cash account identifier (must equal CashAccount.id).
        - name: pageSize
          in: query
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 500
            default: 50
          description: Page size (default 50, max 500).
        - name: pageToken
          in: query
          required: false
          schema:
            type: string
          description: >-
            Opaque pagination cursor from pagination.nextPageToken of the
            previous response.
      responses:
        '200':
          description: >-
            Successful response with transaction results and pagination
            metadata.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CashAccountTransactionsResponse'
              example:
                results:
                  - id: '12345'
                    accountId: f0995efc-25a1-465e-bec3-d309aaf00ede
                    transactionType: card
                    transactionSubtype: cardPayment
                    direction: debit
                    status: settled
                    amount: '100.00'
                    currency: USD
                    originalAmount: '90.00'
                    originalCurrency: EUR
                    conversionRate: '1.1111'
                    postedAt: '2026-05-03T10:16:12Z'
                    counterparty:
                      name: Acme Store
                      type: merchant
                    cardTransactionDetails:
                      cardId: '101'
                      merchantName: Acme Store
                      country: US
                      authorizationStatus: normal
                    bankTransferTransactionDetails: null
                    internalTransferTransactionDetails: null
                pagination:
                  pageSize: 50
                  nextPageToken: eyJsYXN0SWQiOjEyMzk1fQ==
                  hasNext: true
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
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FiatbackApi_PublicErrorResponse'
        '404':
          description: Account not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FiatbackApi_PublicErrorResponse'
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
        '500':
          description: Internal Server Error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FiatbackApi_PublicErrorResponse'
      security:
        - oauth2:
            - etoro-public:money.cash-transactions:read
components:
  schemas:
    CashAccountTransactionsResponse:
      type: object
      required:
        - results
        - pagination
      properties:
        results:
          type: array
          items:
            $ref: '#/components/schemas/CashAccountTransaction'
        pagination:
          $ref: '#/components/schemas/PaginationCursor'
    FiatbackApi_PublicErrorResponse:
      type: object
      description: Error response with code and message
      required:
        - errorCode
        - errorMessage
      properties:
        errorCode:
          type: string
          description: Machine-readable error code
          example: GeneralError
        errorMessage:
          type: string
          description: Human-readable error message
          example: Internal server error. Please retry or contact support
    CashAccountTransaction:
      type: object
      required:
        - id
        - accountId
        - transactionType
        - transactionSubtype
        - direction
        - status
        - amount
        - currency
        - postedAt
      properties:
        id:
          type: string
        accountId:
          type: string
        transactionType:
          type: string
          enum:
            - card
            - internalTransfer
            - bankTransfer
            - balanceAdjustment
        transactionSubtype:
          type: string
          enum:
            - unknown
            - cardPayment
            - contactless
            - onlinePayment
            - cashWithdrawal
            - transferReceived
            - transfer
            - paymentReceived
            - payment
            - refund
            - fee
            - creditBalanceAdjustment
            - debitBalanceAdjustment
            - directDebit
            - cryptoToFiat
        direction:
          type: string
          enum:
            - debit
            - credit
        status:
          type: string
          enum:
            - failed
            - authorized
            - settled
            - rejected
            - returned
            - expired
            - unknown
        amount:
          type: string
          description: Decimal amount as string
        currency:
          type: string
          description: ISO 4217 alphabetic currency code
        originalAmount:
          type: string
          nullable: true
        originalCurrency:
          type: string
          nullable: true
        conversionRate:
          type: string
          nullable: true
        postedAt:
          type: string
          format: date-time
        counterparty:
          $ref: '#/components/schemas/Counterparty'
        cardTransactionDetails:
          $ref: '#/components/schemas/CardTransactionDetails'
          nullable: true
        bankTransferTransactionDetails:
          $ref: '#/components/schemas/BankTransferDetails'
          nullable: true
        internalTransferTransactionDetails:
          $ref: '#/components/schemas/InternalTransferDetails'
          nullable: true
    PaginationCursor:
      type: object
      required:
        - pageSize
        - hasNext
      properties:
        pageSize:
          type: integer
        nextPageToken:
          type: string
          nullable: true
        hasNext:
          type: boolean
    Counterparty:
      type: object
      properties:
        name:
          type: string
        type:
          type: string
          enum:
            - merchant
            - bank_account
            - internal_account
            - unknown
    CardTransactionDetails:
      type: object
      properties:
        cardId:
          type: string
        merchantName:
          type: string
        country:
          type: string
        authorizationStatus:
          type: string
          enum:
            - unknown
            - normal
            - preAuthorize
            - finalAuthorize
            - incremental
            - instalment
            - preferredCustomer
            - recurring
            - delayedCharges
            - noShow
            - authorizeAdvice
            - refund
            - reversal
            - sysReversal
            - accountFunding
    BankTransferDetails:
      type: object
      properties:
        bankIdentifier:
          type: array
          items:
            $ref: '#/components/schemas/BankIdentifierEntry'
        description:
          type: string
        paymentReference:
          type: string
    InternalTransferDetails:
      type: object
      required:
        - transferId
      properties:
        transferId:
          type: string
    BankIdentifierEntry:
      type: object
      required:
        - name
        - value
      properties:
        name:
          type: string
        value:
          type: string
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