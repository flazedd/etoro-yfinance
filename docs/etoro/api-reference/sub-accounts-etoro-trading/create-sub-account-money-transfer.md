> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create Sub-Account Money Transfer

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Executes a money transfer between the authenticated caller and the sub-account identified by the x-sub-account-id header. The amount must be positive with up to two decimal places. Direction ToSubAccount moves funds from the caller to the sub-account; FromSubAccount moves funds from the sub-account back to the caller.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/sub-accounts/etoro-trading/money-transfers
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
  /api/v1/sub-accounts/etoro-trading/money-transfers:
    post:
      tags:
        - Sub Accounts eToro Trading
      summary: Create Sub-Account Money Transfer
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Executes a money transfer between the authenticated caller and the
        sub-account identified by the x-sub-account-id header. The amount must
        be positive with up to two decimal places. Direction ToSubAccount moves
        funds from the caller to the sub-account; FromSubAccount moves funds
        from the sub-account back to the caller.
      operationId: createSubAccountMoneyTransfer
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 3918b535-8d80-49cf-8eec-ad77d185dc4d
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
        - name: x-sub-account-id
          in: header
          required: true
          schema:
            type: string
          description: >-
            The encrypted sub-account identifier. The backend validates that it
            decrypts to a sub-account owned by the caller's token gcid and
            resolves the target compensation CID.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EtoroTradingSubAccountsMoneyTransferRequest'
      responses:
        '200':
          description: The transfer was accepted
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
          description: Bad Request
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              examples:
                RequestBodyIsRequired:
                  summary: Request body is missing
                  value:
                    errorCode: RequestBodyIsRequired
                    errorMessage: Request body is required
                InvalidSubAccountId:
                  summary: Missing, malformed, or undecryptable x-sub-account-id header
                  value:
                    errorCode: InvalidSubAccountId
                    errorMessage: Invalid Sub Account Id
                InvalidAmountInUsd:
                  summary: Amount is not positive or has more than two decimal places
                  value:
                    errorCode: InvalidAmountInUsd
                    errorMessage: AmountInUsd must be a positive number
                InvalidDirection:
                  summary: Direction is not a recognised value
                  value:
                    errorCode: InvalidDirection
                    errorMessage: >-
                      Direction must be ToSubAccount, FromSubAccount,
                      FromStsTokenCidToBodyCid, or FromBodyCidToStsTokenCid
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              example:
                errorCode: Unauthorized
                errorMessage: Unauthorized
        '403':
          description: >-
            Forbidden — the sub-account's gcid does not match the caller's token
            gcid
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              example:
                errorCode: Forbidden
                errorMessage: Forbidden
        '429':
          description: >-
            Too Many Requests — the money-transfer dependency is throttling
            requests
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              example:
                errorCode: MoneyTransferThrottled
                errorMessage: Money transfer is throttled
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
          description: Internal Server Error — the transfer could not be completed
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              example:
                errorCode: MoneyTransferFailed
                errorMessage: Money transfer could not be completed
      security:
        - oauth2:
            - etoro-public:money:transfer
components:
  schemas:
    EtoroTradingSubAccountsMoneyTransferRequest:
      type: object
      properties:
        amountInUsd:
          type: number
          description: >-
            The money-transfer amount in USD. Must be positive and have up to
            two decimal places.
          example: 250.55
        direction:
          type: string
          enum:
            - FromSubAccount
            - ToSubAccount
          description: >-
            The transfer direction. ToSubAccount moves funds from the caller to
            the sub-account; FromSubAccount moves funds from the sub-account
            back to the caller. Parsing is case-insensitive.
          example: ToSubAccount
      required:
        - amountInUsd
        - direction
    EtoroTradingSubAccountsOperationsApi_ErrorResponse:
      type: object
      properties:
        errorCode:
          type: string
        errorMessage:
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