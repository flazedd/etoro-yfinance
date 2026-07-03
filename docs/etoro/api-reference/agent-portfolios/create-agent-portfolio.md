> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create Agent Portfolio

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

[DEPRECATED — use POST /api/v2/agent-portfolios (scope names) instead] Creates a new agent-portfolio — a dedicated user account that receives its own fixed virtual balance (returned in agentPortfolioVirtualBalance). IMPORTANT: investmentAmountInUsd is the amount deducted from YOUR (the caller's) account balance to copy-trade this agent-portfolio — it is NOT the agent-portfolio's own balance. Positions are mirrored proportionally: e.g. if you invest $2,000 and agentPortfolioVirtualBalance is $10,000, each position is copied at 20% of its size into your account.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/agent-portfolios
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
  /api/v1/agent-portfolios:
    post:
      tags:
        - Agent Portfolios
      summary: Create Agent Portfolio
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        [DEPRECATED — use POST /api/v2/agent-portfolios (scope names) instead]
        Creates a new agent-portfolio — a dedicated user account that receives
        its own fixed virtual balance (returned in
        agentPortfolioVirtualBalance). IMPORTANT: investmentAmountInUsd is the
        amount deducted from YOUR (the caller's) account balance to copy-trade
        this agent-portfolio — it is NOT the agent-portfolio's own balance.
        Positions are mirrored proportionally: e.g. if you invest $2,000 and
        agentPortfolioVirtualBalance is $10,000, each position is copied at 20%
        of its size into your account.
      operationId: createAgentPortfolio
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 15cb67a3-65a5-4f99-ac94-06ee27048f29
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
              $ref: '#/components/schemas/CreateAgentPortfolioRequest'
      responses:
        '201':
          description: Agent-portfolio and user token created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateAgentPortfolioResponse'
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
        '207':
          description: Agent-portfolio created but user token provisioning failed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateAgentPortfolioPartialResponse'
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
                NameTooShort:
                  summary: Agent-portfolio name too short
                  value:
                    errorCode: ValidationFailed
                    errorMessage: Agent-portfolio name must be between 6 and 10 characters
                InvestmentBelowMinimum:
                  summary: Investment amount below minimum
                  value:
                    errorCode: ValidationFailed
                    errorMessage: Investment amount is below the minimum threshold
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
              example:
                errorCode: Unauthorized
                errorMessage: Unauthorized
        '429':
          description: Too Many Requests
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AgentPortfolioApi_ErrorResponse'
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
    CreateAgentPortfolioRequest:
      type: object
      properties:
        investmentAmountInUsd:
          type: number
          description: >-
            The amount in USD deducted from the CALLER's account balance to
            copy-trade this agent-portfolio. This is NOT the agent-portfolio's
            own balance — the agent-portfolio receives a separate fixed virtual
            balance (returned as agentPortfolioVirtualBalance). Positions are
            mirrored proportionally: e.g. $2,000 with a $10,000 virtual balance
            = 20% position sizing.
          example: 2000
        agentPortfolioName:
          type: string
          description: A unique display name for the agent-portfolio (6-10 characters).
          example: MyPort1
        agentPortfolioDescription:
          type: string
          description: >-
            An optional description of the agent-portfolio's purpose or
            strategy.
          example: My trading portfolio
        userTokenName:
          type: string
          description: >-
            A human-readable name for the user token provisioned with the
            agent-portfolio.
          example: my-trading-token
        scopeIds:
          type: array
          items:
            type: integer
          deprecated: true
          description: >-
            [DEPRECATED — use scopeNames instead] The set of permission scope
            identifiers to grant to the provisioned user token. Available
            scopes: 200 = etoro-public:real:read, 201 = etoro-public:demo:read,
            202 = etoro-public:real:write, 203 = etoro-public:demo:write.
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
          description: >-
            An optional set of IPv4 addresses allowed to use the provisioned
            user token.
          example:
            - 192.168.1.1
        expiresAt:
          type: string
          format: date-time
          description: >-
            An optional expiration date and time (UTC) for the provisioned user
            token.
          example: '2026-12-31T23:59:59Z'
      required:
        - investmentAmountInUsd
        - agentPortfolioName
        - userTokenName
    CreateAgentPortfolioResponse:
      type: object
      properties:
        agentPortfolioId:
          type: string
          format: uuid
          description: The unique identifier of the newly created agent-portfolio.
          example: a1b2c3d4-e5f6-7890-abcd-ef1234567890
        agentPortfolioName:
          type: string
          description: The display name assigned to the agent-portfolio.
          example: MyPort1
        agentPortfolioGcid:
          type: integer
          description: The GCID associated with the agent-portfolio.
          example: 12345678
        agentPortfolioVirtualBalance:
          type: number
          description: >-
            The fixed virtual balance (in USD) that the agent-portfolio was
            funded with. The investmentAmountInUsd used to copy is proportional
            to this balance.
          example: 10000
        mirrorId:
          type: integer
          description: The Trading API mirror ID for this agent-portfolio's copy trade.
          example: 12345
        userTokens:
          type: array
          items:
            $ref: '#/components/schemas/CreateAgentPortfolioUserTokenItem'
          description: The user tokens generated during agent-portfolio creation.
    CreateAgentPortfolioPartialResponse:
      type: object
      properties:
        agentPortfolioId:
          type: string
          format: uuid
          description: The unique identifier of the newly created agent-portfolio.
          example: a1b2c3d4-e5f6-7890-abcd-ef1234567890
        agentPortfolioName:
          type: string
          description: The display name assigned to the agent-portfolio.
          example: MyPort1
        agentPortfolioGcid:
          type: integer
          description: The GCID associated with the agent-portfolio.
          example: 12345678
        agentPortfolioVirtualBalance:
          type: integer
          description: >-
            The fixed virtual balance (in USD) that the agent-portfolio was
            funded with. The investmentAmountInUsd used to copy is proportional
            to this balance.
          example: 10000
        mirrorId:
          type: integer
          description: The Trading API mirror ID for this agent-portfolio's copy trade.
          example: 12345
        userTokenCreated:
          type: boolean
          description: Always false — indicates that the user token was not created.
          example: false
    AgentPortfolioApi_ErrorResponse:
      type: object
      properties:
        errorCode:
          type: string
        errorMessage:
          type: string
    CreateAgentPortfolioUserTokenItem:
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
          description: The user-defined name for the user token.
          example: my-trading-token
        clientId:
          type: string
          format: uuid
          description: The OAuth client identifier associated with the user token.
          example: c1d2e3f4-a5b6-7890-cdef-123456789abc
        ipsWhitelist:
          type: array
          items:
            type: string
          description: The set of whitelisted IP addresses authorized to use this token.
          example:
            - 192.168.1.1
        scopeIds:
          type: array
          items:
            type: integer
          deprecated: true
          description: >-
            [DEPRECATED — use scopeNames instead] The set of permission scope
            identifiers granted to this token. Available scopes: 200 =
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
        expiresAt:
          type: string
          format: date-time
          description: The expiration date and time of the user token in UTC.
          example: '2026-12-31T23:59:59Z'
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