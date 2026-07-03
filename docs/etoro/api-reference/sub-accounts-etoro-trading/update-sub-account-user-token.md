> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Update Sub-Account User Token

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Updates an existing sub-account user token's scopes, IP whitelist, or expiration. At least one field must be provided.



## OpenAPI

````yaml /api-reference/openapi.json patch /api/v1/sub-accounts/etoro-trading/user-tokens/{userTokenId}
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
  /api/v1/sub-accounts/etoro-trading/user-tokens/{userTokenId}:
    patch:
      tags:
        - Sub Accounts eToro Trading
      summary: Update Sub-Account User Token
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Updates an existing sub-account user token's scopes, IP whitelist, or
        expiration. At least one field must be provided.
      operationId: updateSubAccountUserToken
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 3af6e3b5-6ef5-4986-b431-06e0a1358774
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
        - name: userTokenId
          in: path
          required: true
          schema:
            type: string
            format: uuid
          description: The unique identifier of the user token to update.
        - name: x-sub-account-id
          in: header
          required: true
          schema:
            type: string
          description: >-
            The encrypted sub-account identifier. The backend validates that it
            decrypts to a sub-account owned by the caller's token gcid.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateSubAccountUserTokenRequest'
      responses:
        '204':
          description: User token updated successfully
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
                ScopeNamesRequired:
                  summary: An explicitly empty scope set was supplied
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
        '404':
          description: The user token does not exist for the sub-account
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
              example:
                errorCode: UserTokenNotFound
                errorMessage: User token not found
        '429':
          description: Too Many Requests — a downstream dependency is throttling requests
          content:
            application/json:
              schema:
                $ref: >-
                  #/components/schemas/EtoroTradingSubAccountsOperationsApi_ErrorResponse
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
    UpdateSubAccountUserTokenRequest:
      type: object
      properties:
        scopeNames:
          type: array
          items:
            type: string
          description: >-
            The replacement scope names. When provided, must be a subset of the
            scopes returned by GET
            /api/v1/sub-accounts/etoro-trading/user-tokens/scopes.
          example:
            - etoro-public:trade.real:read
        ipsWhitelist:
          type: array
          items:
            type: string
          description: The replacement IPv4 whitelist.
          example:
            - 192.168.1.1
        expiresAt:
          type: string
          format: date-time
          description: The replacement UTC expiration.
          example: '2026-12-31T23:59:59Z'
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