> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get authenticated user profile

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Returns the profile of the currently authenticated user, including account identifiers (GCID, real and demo CIDs), profile fields from Scope Data API (username, name, player level, gender, language, date of birth, avatar URL), and the OAuth scopes granted to the current access token.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/me
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
  /api/v1/me:
    get:
      tags:
        - Identity
      summary: Get authenticated user profile
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Returns the profile of the currently authenticated user, including
        account identifiers (GCID, real and demo CIDs), profile fields from
        Scope Data API (username, name, player level, gender, language, date of
        birth, avatar URL), and the OAuth scopes granted to the current access
        token.
      operationId: getMe
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: df72ee44-b863-489a-b546-f204fde5d8b4
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
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/meResponse'
              examples:
                example:
                  summary: User Profile Response
                  value:
                    gcid: 123456
                    realCid: 789012
                    demoCid: 345678
                    username: johndoe
                    firstName: John
                    middleName: Q
                    lastName: Doe
                    playerLevel: 3
                    gender: 1
                    language: 1
                    dateOfBirth: '1990-01-01'
                    avatarUrl: >-
                      https://etoro-cdn.etorostatic.com/avatars/150X150/johndoe.jpg
                    scopes:
                      - etoro-public:real:read
                      - etoro-public:user-info:read
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
          description: Unauthorized - Missing or invalid authentication credentials
        '403':
          description: Forbidden - Insufficient permissions
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
        - oauth2:
            - etoro-public:real:write
        - oauth2:
            - etoro-public:demo:write
        - oauth2:
            - etoro-public:user-info:read
components:
  schemas:
    meResponse:
      type: object
      description: >-
        Profile of the authenticated user across eToro account types, including
        granted OAuth scopes.
      required:
        - gcid
        - realCid
        - demoCid
        - username
        - playerLevel
        - gender
        - language
        - dateOfBirth
        - scopes
      properties:
        gcid:
          type: integer
          description: >-
            Global Customer ID - the unique identifier for the user across all
            eToro systems.
        realCid:
          type: integer
          description: >-
            Real account Customer ID - the identifier for the user's real
            trading account.
        demoCid:
          type: integer
          description: >-
            Demo account Customer ID - the identifier for the user's
            virtual/demo trading account.
        username:
          type: string
          description: The user's unique username.
        firstName:
          type: string
          nullable: true
          description: The user's first name.
        middleName:
          type: string
          nullable: true
          description: The user's middle name.
        lastName:
          type: string
          nullable: true
          description: The user's last name.
        playerLevel:
          type: integer
          description: >-
            Player level. Possible values: 1 (Bronze), 2 (Platinum), 3 (Gold), 4
            (Internal), 5 (Silver), 6 (PlatinumPlus), 7 (Diamond).
        gender:
          type: integer
          description: 'Gender. Possible values: 0 (Unknown), 1 (Male), 2 (Female).'
        language:
          type: integer
          description: Language ID (e.g. 1 = English, 2 = German).
        dateOfBirth:
          type: string
          description: Date of birth.
        avatarUrl:
          type: string
          nullable: true
          description: Absolute URL of the user's profile avatar image.
        scopes:
          type: array
          description: OAuth scopes granted to the authenticated token.
          items:
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