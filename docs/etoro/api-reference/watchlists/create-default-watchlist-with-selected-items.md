> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create default watchlist with selected items

> **Rate limit:** 20 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `DELETE /api/v1/watchlists/{watchlistId}`
- `DELETE /api/v1/watchlists/{watchlistId}/items`
- `POST /api/v1/watchlists`
- `POST /api/v1/watchlists/newasdefault-watchlist`
- `POST /api/v1/watchlists/{watchlistId}/items`
- `PUT /api/v1/watchlists/rank/{watchlistId}`
- `PUT /api/v1/watchlists/setUserSelectedUserDefault/{watchlistId}`
- `PUT /api/v1/watchlists/{watchlistId}`
- `PUT /api/v1/watchlists/{watchlistId}/items`

---

Creates a default watchlist populated with the specified items.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/watchlists/default-watchlist/selected-items
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
  /api/v1/watchlists/default-watchlist/selected-items:
    post:
      tags:
        - Watchlists
      summary: Create default watchlist with selected items
      description: >-
        **Rate limit:** 20 requests per 60 seconds. This is a **shared quota** —
        the same budget is consumed by a group of related endpoints, so calling
        any of them reduces what is left for the others (you cannot call each at
        the full rate independently). Endpoints sharing this quota:

        - `DELETE /api/v1/watchlists/{watchlistId}`

        - `DELETE /api/v1/watchlists/{watchlistId}/items`

        - `POST /api/v1/watchlists`

        - `POST /api/v1/watchlists/newasdefault-watchlist`

        - `POST /api/v1/watchlists/{watchlistId}/items`

        - `PUT /api/v1/watchlists/rank/{watchlistId}`

        - `PUT /api/v1/watchlists/setUserSelectedUserDefault/{watchlistId}`

        - `PUT /api/v1/watchlists/{watchlistId}`

        - `PUT /api/v1/watchlists/{watchlistId}/items`


        ---


        Creates a default watchlist populated with the specified items.
      operationId: postWatchlistsDefaultWatchlistSelectedItems
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 922a72dd-259d-4650-9828-7347b362a487
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
        description: Items to include in the default watchlist
        required: true
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/WatchlistItemDto'
      responses:
        '201':
          description: Default watchlist created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WatchlistsResponse'
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 10 endpoints (it is NOT per-endpoint): a request
                to any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
              schema:
                type: integer
              example: 20
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
              example: 20;w=60
        '429':
          description: >-
            Too Many Requests — the shared rate limit (20 requests / 60s) was
            exceeded.
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 10 endpoints (it is NOT per-endpoint): a request
                to any endpoint in the group spends the same budget. See this
                operation's description for the full list of endpoints sharing
                it.
              schema:
                type: integer
              example: 20
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
              example: 20;w=60
            Retry-After:
              description: Seconds to wait before retrying.
              schema:
                type: integer
              example: 60
      security:
        - oauth2:
            - etoro-public:demo:write
        - oauth2:
            - etoro-public:real:write
        - oauth2:
            - etoro-public:watchlist:write
components:
  schemas:
    WatchlistItemDto:
      type: object
      description: Represents an item in a watchlist
      required:
        - itemId
        - itemType
      properties:
        itemId:
          type: integer
          format: int32
          description: Unique identifier of the financial instrument
          example: 12345
        itemType:
          type: string
          description: Type of the financial instrument (e.g., 'Instrument', 'Person')
          example: Instrument
        itemRank:
          type: integer
          format: int32
          description: Ranking position of the item in the watchlist
          default: 0
          example: 1
        itemAddedReason:
          type: string
          description: Reason the item was added to the watchlist
          example: Manual
        itemAddedDate:
          type: string
          format: date-time
          description: Date and time the item was added
        market:
          type: object
          description: Market metadata for the instrument when included
          properties:
            id:
              type: string
            symbolName:
              type: string
            displayName:
              type: string
            assetTypeId:
              type: integer
              format: int32
            assetTypeSubCategoryId:
              type: integer
              format: int32
              nullable: true
            exchangeId:
              type: integer
              format: int32
            hasExpirationDate:
              type: boolean
            avatar:
              type: object
              properties:
                small:
                  type: string
                medium:
                  type: string
                large:
                  type: string
                svg:
                  type: object
                  nullable: true
                  description: SVG avatar with background and text colors
                  properties:
                    url:
                      type: string
                    backgroundColor:
                      type: string
                    textColor:
                      type: string
    WatchlistsResponse:
      type: object
      description: Response containing multiple watchlists with metadata
      properties:
        status:
          type: integer
          format: int32
          description: HTTP status code of the response
          example: 200
        watchlists:
          type: array
          description: List of user watchlists
          items:
            $ref: '#/components/schemas/WatchlistResponse'
        exception:
          type: object
          description: Exception details when the request partially failed
          properties:
            invalidItems:
              type: array
              description: List of invalid item identifiers
              items:
                type: string
            reason:
              type: string
              description: Reason for the exception
            message:
              type: string
              description: Human-readable exception message
        meta:
          type: object
          description: Response metadata including pagination info
          properties:
            pageNumber:
              type: integer
              format: int32
              description: Current page number
              example: 0
            itemsPerPage:
              type: integer
              format: int32
              description: Number of items per page
              example: 100
            maxItemsInWatchlistLimit:
              type: integer
              format: int32
              description: Maximum allowed items per watchlist
              example: 1000
            maxWatchlistsLimit:
              type: integer
              format: int32
              description: Maximum allowed watchlists per user
              example: 10
        isSucceeded:
          type: boolean
          description: Whether the request succeeded
          example: true
    WatchlistResponse:
      type: object
      description: Represents a watchlist with its metadata and items
      properties:
        watchlistId:
          type: string
          description: Unique identifier of the watchlist
          example: '12345'
        name:
          type: string
          description: Display name of the watchlist
          example: Tech Watchlist
        Gcid:
          type: integer
          format: int32
          description: Global Customer ID of the watchlist owner
          example: 12345
        watchlistType:
          type: string
          enum:
            - Static
            - Dynamic
            - RecentlyInvested
            - Default
          description: Type of the watchlist
          example: Static
        totalItems:
          type: integer
          format: int32
          description: Total number of items in the watchlist
          example: 100
        isDefault:
          type: boolean
          description: Whether this is a default system watchlist
          example: true
        isUserSelectedDefault:
          type: boolean
          description: Whether this is the user's selected default watchlist
          example: true
        watchlistRank:
          type: integer
          format: int32
          description: Display order rank of the watchlist
          example: 1
        dynamicUrl:
          type: string
          nullable: true
          description: URL for dynamic watchlist queries
        items:
          type: array
          description: Items contained in the watchlist
          items:
            $ref: '#/components/schemas/WatchlistItemDto'
          example:
            - itemId: 12345
              itemType: Instrument
              itemRank: 1
        relatedAssets:
          type: array
          description: Related asset IDs
          nullable: true
          items:
            type: integer
            format: int32
          example:
            - 12345
            - 67890
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