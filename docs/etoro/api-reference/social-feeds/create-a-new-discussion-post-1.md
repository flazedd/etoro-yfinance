> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create a new discussion post

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Creates a new discussion post in the feed system. This endpoint allows users to create posts that can be associated with instruments, users, or general discussions.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/posts
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
  /api/v1/posts:
    post:
      tags:
        - Social Feeds
      summary: Create a new discussion post
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Creates a new discussion post in the feed system. This endpoint allows
        users to create posts that can be associated with instruments, users, or
        general discussions.
      operationId: postPosts
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 66d248c0-d6fe-43de-a849-2df99f8f2ce8
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
        description: Discussion post creation details
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DiscussionCreateRequest'
      responses:
        '201':
          description: Post created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Post'
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
          description: Authentication required
        '403':
          description: User is blocked
        '422':
          description: >-
            Validation error — content rejected (e.g. by the spam classifier) or
            fields contain invalid data
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
            - etoro-public:feed:write
components:
  schemas:
    DiscussionCreateRequest:
      type: object
      description: Request body for creating a new discussion post
      properties:
        message:
          type: string
          description: Post text content (max 1000 chars)
          example: Just opened a long position on $TSLA — strong earnings ahead!
        attachments:
          $ref: '#/components/schemas/Attachments'
    Post:
      type: object
      description: A feed post returned by create / update / get-by-ID
      properties:
        id:
          type: string
          description: Unique post ID
          example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        owner:
          $ref: '#/components/schemas/User'
        obsoleteId:
          type: string
          description: Legacy numeric post ID
          example: '12345'
        created:
          type: string
          format: date-time
          description: Creation timestamp
          example: '2025-01-15T10:30:00Z'
        message:
          type: object
          description: Post/comment text content
          properties:
            text:
              type: string
              description: Text content
              example: Excited about $TSLA earnings next week!
            languageCode:
              type: string
              description: BCP-47 language code
              example: en
        updated:
          type: string
          format: date-time
          nullable: true
          description: Last-edited timestamp
          example: '2025-01-16T08:00:00Z'
        isDeleted:
          type: boolean
          description: True when the post has been soft-deleted
          example: false
        type:
          type: string
          enum:
            - Default
            - Share
            - MarketEvent
            - Trade
            - Order
            - Copy
            - Poll
            - Article
          description: Post type
          example: Default
        metadata:
          type: object
          description: Post type–specific metadata — only the relevant key is populated
          properties:
            share:
              type: object
              description: Share metadata — present when type is Share
              properties:
                sharedPost:
                  $ref: '#/components/schemas/Post'
                sharedOriginPost:
                  $ref: '#/components/schemas/Post'
            marketEvent:
              type: object
              description: Market event metadata — present when type is MarketEvent
              properties:
                earningReportId:
                  type: integer
                  description: Earnings report ID
                  example: 1042
                market:
                  $ref: '#/components/schemas/Market'
                stocksIndustryId:
                  type: integer
                  description: Industry sector ID
                  example: 15
                earningsDate:
                  type: string
                  format: date-time
                  description: Earnings announcement date
                  example: '2025-01-15T10:30:00Z'
                isBeforeMarketOpen:
                  type: boolean
                  description: Event occurs before market open
                  example: true
                earningsYear:
                  type: integer
                  description: Fiscal year of earnings
                  example: 2025
                earningsQuarter:
                  type: integer
                  description: Fiscal quarter (1–4)
                  example: 1
                verified:
                  type: boolean
                  description: Whether the event data is verified
                  example: true
                marketCap:
                  type: number
                  format: double
                  description: Market capitalisation in USD
                  example: 800000000000
                estimatedEps:
                  type: number
                  format: double
                  description: Estimated earnings per share
                  example: 1.42
                estimatedSales:
                  type: number
                  format: double
                  description: Estimated revenue in USD
                  example: 25000000000
                tagName:
                  type: string
                  enum:
                    - Reports
                    - Dividends
                    - Split
                    - ReverseSplit
                  description: Event tag
                  example: Reports
                textKey:
                  type: integer
                  description: Localisation key for event label
                  example: 3
            trade:
              type: object
              description: Trade metadata — present when type is Trade
              properties:
                type:
                  type: string
                  enum:
                    - Open
                    - Close
                  description: Trade lifecycle stage
                  example: Open
                positionId:
                  type: integer
                  description: Internal position ID
                  example: 987654321
                market:
                  $ref: '#/components/schemas/Market'
                gain:
                  type: number
                  format: float
                  description: P&L gain/loss percentage
                  example: 12.5
                rate:
                  type: number
                  format: float
                  description: Entry/exit rate
                  example: 245.3
                direction:
                  type: string
                  enum:
                    - Long
                    - Short
                  description: Trade direction
                  example: Long
            order:
              type: object
              description: Order metadata — present when type is Order
              properties:
                type:
                  type: string
                  enum:
                    - Open
                    - Close
                  description: Order lifecycle stage
                  example: Open
                orderId:
                  type: integer
                  description: Internal order ID
                  example: 123456789
                market:
                  $ref: '#/components/schemas/Market'
                rate:
                  type: number
                  format: float
                  description: Limit/entry rate
                  example: 240
                direction:
                  type: string
                  enum:
                    - Long
                    - Short
                  description: Order direction
                  example: Long
            copy:
              type: object
              description: Copy metadata — present when type is Copy
              properties:
                type:
                  type: string
                  enum:
                    - Start
                    - Stop
                  description: Copy event type
                  example: Start
                user:
                  $ref: '#/components/schemas/User'
            poll:
              type: object
              description: Poll metadata — present when type is Poll
              properties:
                id:
                  type: integer
                  description: Poll ID
                  example: 55
                title:
                  type: string
                  description: Poll question
                  example: Where do you see $TSLA by year-end?
                gcid:
                  type: integer
                  description: Poll creator GCID
                  example: 7890
                options:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: Option ID
                        example: 1
                      index:
                        type: integer
                        description: >-
                          Display order (1-based, matches the index supplied at
                          poll creation)
                        example: 1
                        minimum: 1
                      text:
                        type: string
                        description: Option label
                        example: Bullish
                      isUserVoted:
                        type: boolean
                        description: Requester voted for this option
                        example: false
                      votesCount:
                        type: integer
                        description: Total votes for this option
                        example: 128
            article:
              type: object
              description: Article metadata — present when post type is Article
              properties:
                id:
                  type: integer
                  description: Article ID
                  example: 9001
                title:
                  type: string
                  description: Article title
                  example: Why TSLA Could Hit $500 This Year
                url:
                  type: string
                  description: Canonical article URL
                  example: >-
                    https://etoro.com/news/markets/articles/why-tsla-could-hit-500
                rating:
                  type: string
                  enum:
                    - Bearish
                    - Bullish
                  nullable: true
                  description: Analyst rating
                  example: Bullish
                featuredImage:
                  $ref: '#/components/schemas/Attachment'
                body:
                  type: string
                  description: Full article HTML body
                  example: <p>Tesla has shown strong fundamentals...</p>
                bodyPreview:
                  type: string
                  description: Plain-text preview (≈200 chars)
                  example: Tesla has shown strong fundamentals this quarter...
                aiSummary:
                  type: string
                  description: AI-generated summary
                  example: >-
                    Analyst argues Tesla's pipeline supports a $500 target by
                    year-end.
                languageCode:
                  type: string
                  description: BCP-47 language code
                  example: en
                status:
                  type: string
                  enum:
                    - Draft
                    - Published
                    - Deleted
                  description: Publication status
                  example: Published
                editStatus:
                  type: string
                  enum:
                    - None
                    - Edited
                    - Moderated
                  description: Edit status
                  example: None
                ownerId:
                  type: integer
                  description: Author's internal user ID
                  example: 7890
                created:
                  type: string
                  format: date-time
                  description: When the article was created
                  example: '2025-01-15T10:30:00Z'
                updated:
                  type: string
                  format: date-time
                  nullable: true
                  description: Last edit timestamp
                  example: '2025-01-16T08:00:00Z'
                published:
                  type: string
                  format: date-time
                  nullable: true
                  description: Publication timestamp
                  example: '2025-01-16T09:00:00Z'
                readingTimeMinutes:
                  type: number
                  format: float
                  description: Estimated reading time
                  example: 3.5
                wordCount:
                  type: integer
                  description: Word count
                  example: 750
        attachments:
          type: array
          items:
            $ref: '#/components/schemas/Attachment'
        tags:
          type: array
          items:
            type: object
            properties:
              market:
                $ref: '#/components/schemas/Market'
        mentions:
          type: array
          items:
            type: object
            properties:
              user:
                $ref: '#/components/schemas/User'
              isDirect:
                type: boolean
                description: Direct @-mention
                example: true
        isSpam:
          type: boolean
          description: True when the post is classified as spam
          example: false
        editStatus:
          type: string
          enum:
            - None
            - Edited
            - Moderated
          description: Edit lifecycle status
          example: None
    Attachments:
      type: array
      description: List of attachments for a post or comment (request body format)
      items:
        type: object
        description: Media or link attachment
        properties:
          url:
            type: string
            description: Full URL of the attachment
            example: https://cdn.etoro.com/rich-media/images/johndoe/abc-2025-01-15.jpg
          title:
            type: string
            description: Title of the attachment
            example: Tesla Q4 Earnings Chart
          host:
            type: string
            description: Host domain of the attachment
            example: cdn.etoro.com
          description:
            type: string
            description: Short description of the attachment
            example: Tesla quarterly earnings breakdown
          mediaType:
            type: string
            enum:
              - None
              - Link
              - Image
            description: Type of media (video not supported for upload)
            example: Image
          media:
            type: object
            description: Media content details (images only)
            properties:
              image:
                type: object
                description: Image dimensions and URL
                properties:
                  width:
                    type: integer
                    description: Width in pixels
                    example: 1200
                  height:
                    type: integer
                    description: Height in pixels
                    example: 630
                  url:
                    type: string
                    description: Image URL
                    example: >-
                      https://cdn.etoro.com/rich-media/images/johndoe/abc-2025-01-15.jpg
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
    Market:
      type: object
      description: Financial instrument / market
      properties:
        id:
          type: string
          description: Market identifier
          example: TSLA
        symbolName:
          type: string
          description: Ticker symbol
          example: TSLA
        displayName:
          type: string
          description: Human-readable name
          example: Tesla
        updated:
          type: string
          format: date-time
          nullable: true
          description: Last update timestamp
          example: '2025-01-15T00:00:00Z'
        assetType:
          type: string
          enum:
            - Stocks
            - Bonds
            - ETF
            - Index
            - Warrants
            - Options
            - Futures
            - CFD
            - TRS
            - FOREX
            - CommodityMetals
            - CommodityEnergyAgriculture
            - CryptoCoin
            - NFT
          description: Asset class
          example: Stocks
        internalId:
          type: integer
          description: Internal numeric market ID
          example: 59114
        avatar:
          type: object
          description: Market logo images
          properties:
            small:
              type: string
              description: Small logo URL (32 px)
              example: https://cdn.etoro.com/assets/img/markets/TSLA/small.png
            medium:
              type: string
              description: Medium logo URL (64 px)
              example: https://cdn.etoro.com/assets/img/markets/TSLA/medium.png
            large:
              type: string
              description: Large logo URL (128 px)
              example: https://cdn.etoro.com/assets/img/markets/TSLA/large.png
            svg:
              type: object
              nullable: true
              description: SVG logo with brand colours
              properties:
                url:
                  type: string
                  description: SVG URL
                  example: https://cdn.etoro.com/assets/img/markets/TSLA/logo.svg
                backgroundColor:
                  type: string
                  description: Brand background colour (hex)
                  example: '#CC0000'
                textColor:
                  type: string
                  description: Brand text colour (hex)
                  example: '#FFFFFF'
        application:
          type: string
          enum:
            - eToro
            - Delta
            - Gatsby
          description: Source application
          example: eToro
        metadata:
          type: string
          description: Opaque JSON metadata string
          example: '{}'
        assetTypeId:
          type: integer
          description: Numeric asset type ID
          example: 10
        assetTypeSubCategoryId:
          type: integer
          description: Numeric asset sub-category ID
          example: 101
    Attachment:
      type: object
      description: Media or link attachment
      properties:
        url:
          type: string
          description: Full URL of the attachment
          example: https://cdn.etoro.com/rich-media/images/johndoe/abc-2025-01-15.jpg
        title:
          type: string
          description: Title of the attachment
          example: Tesla Q4 Earnings Chart
        host:
          type: string
          description: Host domain of the attachment
          example: cdn.etoro.com
        description:
          type: string
          description: Short description of the attachment
          example: Tesla quarterly earnings breakdown
        mediaType:
          type: string
          enum:
            - None
            - Link
            - Image
            - Video
          description: Type of media
          example: Image
        media:
          type: object
          description: Media content details
          properties:
            image:
              type: object
              description: Image dimensions and URL
              properties:
                width:
                  type: integer
                  description: Width in pixels
                  example: 1200
                height:
                  type: integer
                  description: Height in pixels
                  example: 630
                url:
                  type: string
                  description: Image URL
                  example: >-
                    https://cdn.etoro.com/rich-media/images/johndoe/abc-2025-01-15.jpg
            video:
              type: object
              description: Video source details
              properties:
                videoSourceId:
                  type: string
                  description: External video ID
                  example: dQw4w9WgXcQ
                videoSource:
                  type: string
                  enum:
                    - None
                    - YouTube
                    - Vimeo
                  description: Video provider
                  example: YouTube
                image:
                  type: object
                  description: Video thumbnail
                  properties:
                    width:
                      type: integer
                      description: Thumbnail width in pixels
                      example: 1280
                    height:
                      type: integer
                      description: Thumbnail height in pixels
                      example: 720
                    url:
                      type: string
                      description: Thumbnail URL
                      example: https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg
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