> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create Sub-Account User Token

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Generates a non-interactive user token for the sub-account identified by the x-sub-account-id header. The secret token value is returned only once, in this response.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/sub-accounts/etoro-trading/user-tokens
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
  /api/v1/sub-accounts/etoro-trading/user-tokens:
    post:
      tags:
        - Sub Accounts eToro Trading
      summary: Create Sub-Account User Token
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Generates a non-interactive user token for the sub-account identified by
        the x-sub-account-id header. The secret token value is returned only
        once, in this response.
      operationId: createSubAccountUserToken
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 291733a1-4234-427a-886e-31a2cffe6c76
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
            generates the token for the sub-account's gcid.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateSubAccountUserTokenRequest'
      responses:
        '201':
          description: User token created successfully
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_CreateUserTokenResponse
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
                UserTokenNameRequired:
                  summary: User token name is missing
                  value:
                    errorCode: UserTokenNameRequired
                    errorMessage: UserTokenName is required
                ScopeNamesRequired:
                  summary: At least one scope name is required
                  value:
                    errorCode: ScopeNamesRequired
                    errorMessage: At least one scope name is required
                InvalidSubAccountId:
                  summary: Missing, malformed, or undecryptable x-sub-account-id header
                  value:
                    errorCode: InvalidSubAccountId
                    errorMessage: Invalid Sub Account Id
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
            Forbidden — a requested scope name is not allowed, or the
            sub-account is not owned by the caller
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              examples:
                ScopeNameNotAllowed:
                  summary: A requested scope name is disallowed or unknown
                  value:
                    errorCode: ScopeNameNotAllowed
                    errorMessage: Scope name not allowed
                Forbidden:
                  summary: >-
                    The sub-account's gcid does not match the caller's token
                    gcid
                  value:
                    errorCode: Forbidden
                    errorMessage: Forbidden
        '409':
          description: >-
            Conflict — a user token with the requested name already exists for
            this sub-account
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              example:
                errorCode: UserKeyNameAlreadyExists
                errorMessage: UserKeyName already exists
        '429':
          description: >-
            Too Many Requests — the per-user token cap was exceeded, or a
            downstream dependency is throttling requests
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              examples:
                MaxUserTokensExceeded:
                  summary: The per-user token cap was exceeded
                  value:
                    errorCode: MaxUserTokensExceeded
                    errorMessage: Maximum number of user tokens exceeded
                TooManyRequests:
                  summary: A downstream dependency is throttling requests
                  value:
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
          description: Internal Server Error
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              example:
                errorCode: UnhandledException
                errorMessage: Global Error
      security:
        - oauth2:
            - etoro-public:sub-accounts:write
components:
  schemas:
    CreateSubAccountUserTokenRequest:
      type: object
      properties:
        userTokenName:
          type: string
          description: A friendly display name for the user token.
          example: my-trading-bot
        scopeNames:
          type: array
          items:
            type: string
          description: >-
            The scope names to assign. Must be a subset of the scopes returned
            by GET /api/v1/sub-accounts/etoro-trading/user-tokens/scopes.
          example:
            - etoro-public:trade.real:read
            - etoro-public:trade.real:write
        ipsWhitelist:
          type: array
          items:
            type: string
          description: An optional IPv4 whitelist for the token.
          example:
            - 192.168.1.1
        expiresAt:
          type: string
          format: date-time
          description: An optional UTC expiration for the token.
          example: '2026-12-31T23:59:59Z'
      required:
        - userTokenName
        - scopeNames
    EtoroTradingSubAccountsOperationsApi_CreateUserTokenResponse:
      type: object
      properties:
        userTokenId:
          type: string
          format: uuid
          description: The unique identifier of the created user token.
          example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        userToken:
          type: string
          description: The secret token value. Returned only once, on creation.
          example: ut_live_9f8c7b6a5d4e3f2a1b0c
        userTokenName:
          type: string
          description: The friendly display name assigned to the token.
          example: my-trading-bot
        clientId:
          type: string
          format: uuid
          description: The OAuth client id associated with the token.
          example: 7c9e6679-7425-40de-944b-e07fc1f90ae7
        ipsWhitelist:
          type: array
          items:
            type: string
          description: The IPv4 addresses the token is restricted to, if any.
          example:
            - 192.168.1.1
        scopes:
          type: array
          items:
            $ref: '#/components/schemas/ScopeNameItem'
          description: The scopes granted to the token.
        expiresAt:
          type: string
          format: date-time
          nullable: true
          description: The UTC expiration of the token, if one was set.
          example: '2026-12-31T23:59:59Z'
        createdAt:
          type: string
          format: date-time
          description: When this user token was created.
          example: '2026-06-06T10:15:00Z'
    EtoroTradingSubAccountsOperationsApi_ErrorResponse:
      type: object
      properties:
        errorCode:
          type: string
        errorMessage:
          type: string
    ScopeNameItem:
      type: object
      properties:
        name:
          type: string
          description: The permission scope name.
          example: etoro-public:trade.real:read
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