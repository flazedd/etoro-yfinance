> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# List shares of a post

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Returns a paginated list of shares of the specified post, including both plain reshares and quote shares. Authentication is optional.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/posts/{postId}/shares
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
  /api/v1/posts/{postId}/shares:
    get:
      tags:
        - Social Feeds
      summary: List shares of a post
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Returns a paginated list of shares of the specified post, including both
        plain reshares and quote shares. Authentication is optional.
      operationId: getPostsByPostIdShares
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: e0c9bfd8-b69e-4a04-84ef-d64b39d0344a
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
        - name: postId
          in: path
          required: true
          description: ID of the post to list shares of (UUID)
          schema:
            type: string
            format: uuid
          example: d9020c00-c364-11ee-8080-80005148990b
        - name: take
          in: query
          description: Number of items to return (1–100, default 20)
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
          example: 20
        - name: offsetEntityId
          in: query
          description: Opaque cursor from a previous response for stable paging
          schema:
            type: string
          example: c3d4e5f6-a7b8-4901-cdef-345678901234
        - name: order
          in: query
          description: Sort order
          schema:
            type: string
            enum:
              - Asc
              - Desc
            default: Desc
          example: Desc
        - name: client_request_id
          in: query
          required: true
          description: >-
            Client-generated correlation ID (UUID). Required for request tracing
            and idempotency.
          schema:
            type: string
            format: uuid
          example: 2b6361e3-079c-42a1-b6d5-4b9c16601ae1
      responses:
        '200':
          description: Paginated list of shares
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SharesResponse'
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
        '404':
          description: Post not found
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
            - etoro-public:feed:read
components:
  schemas:
    SharesResponse:
      type: object
      description: Paginated list of shares on a post
      properties:
        paging:
          type: object
          description: Pagination info
          properties:
            totalCount:
              type: integer
              description: Total number of shares
              example: 17
            offsetEntityId:
              type: string
              description: Opaque cursor for next page
              example: c3d4e5f6-a7b8-4901-cdef-345678901234
            next:
              type: string
              description: URL to fetch the next page
              example: >-
                /api/v1/feeds/post/d9020c00-c364-11ee-8080-80005148990b/shares?take=20&offsetEntityId=c3d4e5f6-a7b8-4901-cdef-345678901234
        postShares:
          type: array
          description: List of share entries
          items:
            type: object
            description: A single share record
            properties:
              shareReactionId:
                type: string
                description: ID of the share reaction
                example: e5f6a7b8-c9d0-4123-efab-567890123456
              createdAt:
                type: string
                format: date-time
                description: When the share was created
                example: '2025-01-15T10:30:00Z'
                nullable: true
              owner:
                $ref: '#/components/schemas/User'
    User:
      type: object
      description: eToro user profile (slim projection)
      properties:
        id:
          type: string
          description: User's GCID (string form)
          example: '7890'
        username:
          type: string
          description: Unique username
          example: johndoe
        firstName:
          type: string
          description: First name
          example: John
        lastName:
          type: string
          description: Last name
          example: Doe
        avatar:
          type: object
          description: Profile picture URLs
          properties:
            small:
              type: string
              description: 32 px avatar URL
              example: https://etoro-cdn.etorostatic.com/avatars/150X150/johndoe.jpg
            medium:
              type: string
              description: 64 px avatar URL
              example: https://etoro-cdn.etorostatic.com/avatars/200X200/johndoe.jpg
            large:
              type: string
              description: 128 px avatar URL
              example: https://etoro-cdn.etorostatic.com/avatars/300X300/johndoe.jpg
            svg:
              type: object
              nullable: true
              description: SVG avatar with brand colours (null when not available)
              properties:
                url:
                  type: string
                  description: SVG URL
                  example: https://etoro-cdn.etorostatic.com/avatars/svg/johndoe.svg
                backgroundColor:
                  type: string
                  description: Background colour hex
                  example: '#2196F3'
                textColor:
                  type: string
                  description: Text colour hex
                  example: '#FFFFFF'
        roles:
          type: array
          description: User roles
          items:
            type: string
            enum:
              - Regular
              - PI
              - Moderator
              - Anonymous
              - eToroTeam
              - eTorian
              - CopyPortfolio
              - Depositor
              - Admin
              - Verified
              - Analyst
          example:
            - Regular
        isBlocked:
          type: boolean
          description: Owner has blocked the requester
          example: false
        isPrivate:
          type: boolean
          description: User's profile is private
          example: false
        countryCode:
          type: integer
          description: ISO numeric country code
          example: 840
        piLevel:
          type: integer
          description: Popular Investor level (0 = not PI)
          example: 0
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