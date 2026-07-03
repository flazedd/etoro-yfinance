> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create User Token

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

[DEPRECATED — use POST /api/v2/agent-portfolios/{agentPortfolioId}/user-tokens (scope names) instead] Creates a new user token for the specified agent-portfolio.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/agent-portfolios/{agentPortfolioId}/user-tokens
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
  /api/v1/agent-portfolios/{agentPortfolioId}/user-tokens:
    post:
      tags:
        - Agent Portfolios
      summary: Create User Token
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        [DEPRECATED — use POST
        /api/v2/agent-portfolios/{agentPortfolioId}/user-tokens (scope names)
        instead] Creates a new user token for the specified agent-portfolio.
      operationId: createAgentPortfolioUserToken
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: bbf73761-9cdd-44d1-b7f6-066f5cf0bdc2
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
        - name: agentPortfolioId
          in: path
          required: true
          schema:
            type: string
            format: uuid
          description: The unique identifier of the agent-portfolio.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserTokenRequest'
      responses:
        '201':
          description: User token created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentPortfolioApi_CreateUserTokenResponse'
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
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
              examples:
                ScopeIdsRequired:
                  summary: Scope IDs are required
                  value:
                    errorCode: ScopeIdsRequired
                    errorMessage: ScopeIds is required
                InvalidIp:
                  summary: Invalid IP address
                  value:
                    errorCode: IpsWhitelistInvalidIp
                    errorMessage: IpsWhitelist contains an invalid IPv4 address
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
              example:
                errorCode: Unauthorized
                errorMessage: Unauthorized
        '404':
          description: Agent-portfolio not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
              example:
                errorCode: NotFound
                errorMessage: Agent-portfolio not found
        '409':
          description: >-
            Conflict — a user token with the requested name already exists for
            this agent-portfolio
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
              example:
                errorCode: UserKeyNameAlreadyExists
                errorMessage: UserKeyName already exists
        '429':
          description: Too Many Requests
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
              example:
                errorCode: MaxUserTokensExceeded
                errorMessage: Maximum number of user tokens exceeded
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
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
              example:
                errorCode: UnhandledException
                errorMessage: Global Error
      deprecated: true
      security:
        - oauth2:
            - etoro-public:real:write
        - oauth2:
            - etoro-public:agent-portfolio:write
components:
  schemas:
    CreateUserTokenRequest:
      type: object
      properties:
        userTokenName:
          type: string
          description: A human-readable name to identify the user token.
          example: my-trading-token
        scopeIds:
          type: array
          items:
            type: integer
          deprecated: true
          description: >-
            [DEPRECATED — use scopeNames instead] The set of permission scope
            identifiers to grant to this token. Available scopes: 200 =
            etoro-public:real:read, 201 = etoro-public:demo:read, 202 =
            etoro-public:real:write, 203 = etoro-public:demo:write.
          example:
            - 211
            - 212
        scopeNames:
          type: array
          items:
            type: string
          description: >-
            The set of permission scope names (preferred; replaces the
            deprecated scopeIds). Provide either scopeNames or scopeIds.
            Available scopes: etoro-public:real:read, etoro-public:demo:read,
            etoro-public:real:write, etoro-public:demo:write.
          example:
            - etoro-public:trade.real:read
            - etoro-public:trade.real:write
        ipsWhitelist:
          type: array
          items:
            type: string
          description: An optional set of IPv4 addresses allowed to use this token.
          example:
            - 192.168.1.1
        expiresAt:
          type: string
          format: date-time
          description: An optional expiration date and time for the token in UTC.
          example: '2026-12-31T23:59:59Z'
      required:
        - userTokenName
    AgentPortfolioApi_CreateUserTokenResponse:
      type: object
      properties:
        userTokenId:
          type: string
          format: uuid
          description: The unique identifier of the newly created user token.
          example: f9e8d7c6-b5a4-3210-fedc-ba9876543210
        userToken:
          type: string
          description: The generated user token secret. Only available at creation time.
          example: sk_live_a1b2c3d4e5f6...
        userTokenName:
          type: string
          description: The display name of the user token.
          example: my-trading-token
        clientId:
          type: string
          format: uuid
          description: >-
            The client identifier of the application the token is associated
            with.
          example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        ipsWhitelist:
          type: array
          items:
            type: string
          description: >-
            The IPv4 addresses from which the token is allowed to be used. Null
            or empty when unrestricted.
          example:
            - 192.168.1.1
        scopeNames:
          type: array
          items:
            type: string
          description: The authorized scope names granted to the token.
          example:
            - etoro-public:trade.real:read
        expiresAt:
          type: string
          format: date-time
          nullable: true
          description: >-
            The UTC expiration date of the token. Null when the token does not
            expire.
          example: '2026-12-31T23:59:59Z'
        createdAt:
          type: string
          format: date-time
          description: The UTC timestamp at which the token was created.
          example: '2026-03-06T12:00:00Z'
    AgentPortfolioApi_ErrorResponse:
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