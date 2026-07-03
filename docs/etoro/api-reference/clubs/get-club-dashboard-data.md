> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get club dashboard data

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Retrieves club dashboard data for the authenticated user, including tier information, benefits, account manager details, offers, downgrade risk, and webinars.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/clubs
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
  /api/v1/clubs:
    get:
      tags:
        - Clubs
      summary: Get club dashboard data
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Retrieves club dashboard data for the authenticated user, including tier
        information, benefits, account manager details, offers, downgrade risk,
        and webinars.
      operationId: getClubs
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: e8579775-e590-44fa-9dda-fa50ebd21570
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
          description: Club dashboard data retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ClubDashboardDataResponse'
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
          description: Unauthorized. Invalid or missing authentication
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ClubsApi_PublicErrorResponse'
              example:
                errorCode: Unauthorized
                errorMessage: Unauthorized
        '403':
          description: Forbidden - insufficient permissions
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ClubsApi_PublicErrorResponse'
              example:
                errorCode: InsufficientPermissions
                errorMessage: Insufficient permissions to access this resource
        '429':
          description: Too Many Requests
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ClubsApi_PublicErrorResponse'
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
                $ref: '#/components/schemas/ClubsApi_PublicErrorResponse'
              example:
                errorCode: UnhandledException
                errorMessage: Global Error
      security:
        - oauth2:
            - etoro-public:club:read
components:
  schemas:
    ClubDashboardDataResponse:
      type: object
      description: Club dashboard data for a user
      properties:
        clubs:
          type: array
          description: List of club tiers with equity thresholds
          items:
            $ref: '#/components/schemas/ClubInfo'
        contacts:
          $ref: '#/components/schemas/ContactsResponse'
          description: Account manager contact information for eligible users
        downgradeRisk:
          $ref: '#/components/schemas/DowngradeRiskResponse'
          description: Club tier downgrade risk assessment
        offers:
          $ref: '#/components/schemas/UserOffersData'
          description: Club benefit offers categorized by tier availability
        webinars:
          $ref: '#/components/schemas/WebinarsResponse'
          description: Upcoming and past club webinars
    ClubsApi_PublicErrorResponse:
      type: object
      description: Standard error response
      required:
        - errorCode
        - errorMessage
      properties:
        errorCode:
          type: string
          description: Machine-readable error code
          example: UnhandledException
        errorMessage:
          type: string
          description: Human-readable error message
          example: Global Error
    ClubInfo:
      type: object
      description: A single club tier with equity thresholds
      properties:
        name:
          type: string
          enum:
            - Internal
            - Bronze
            - Silver
            - Gold
            - Platinum
            - PlatinumPlus
            - Diamond
          description: Display name of the club tier
          example: Silver
        minRealizedEquity:
          type: integer
          nullable: true
          description: Minimum realized equity threshold for this tier
          example: 5000
        maxRealizedEquity:
          type: integer
          nullable: true
          description: Maximum realized equity threshold for this tier
          example: 10000
        rank:
          type: integer
          description: Display rank of this tier
          example: 2
    ContactsResponse:
      type: object
      description: Account manager contact details
      properties:
        manager:
          $ref: '#/components/schemas/ContactInfo'
          nullable: true
          description: Assigned account manager profile
    DowngradeRiskResponse:
      type: object
      description: Club tier downgrade risk assessment
      properties:
        isAtRisk:
          type: boolean
          description: Whether the user is at risk of club tier downgrade
          example: false
        daysUntilDowngrade:
          type: integer
          nullable: true
          description: >-
            Days remaining until potential downgrade. Present only when isAtRisk
            is true.
          example: 30
    UserOffersData:
      type: object
      description: Club offers categorized by availability
      properties:
        currentPlayerLevelAvailableOffers:
          type: array
          description: Offers available at the user's current club tier
          items:
            $ref: '#/components/schemas/ClubOffer'
        nextPlayerLevelAvailableOffers:
          type: array
          description: Offers that become available at the next club tier
          items:
            $ref: '#/components/schemas/ClubOffer'
        staticEligibleOffers:
          type: array
          description: Offers eligible across specific club tiers
          items:
            $ref: '#/components/schemas/StaticEligibleOffer'
    WebinarsResponse:
      type: object
      description: Upcoming and past webinars
      properties:
        upcomingWebinars:
          type: array
          description: List of upcoming webinars the user can join
          items:
            $ref: '#/components/schemas/Webinar'
        previousWebinars:
          type: array
          description: List of past webinars with recordings
          items:
            $ref: '#/components/schemas/Webinar'
    ContactInfo:
      type: object
      description: Account manager profile
      properties:
        firstName:
          type: string
          description: Account manager first name
          example: John
        lastName:
          type: string
          description: Account manager last name
          example: Smith
        email:
          type: string
          format: email
          description: Account manager email address
          example: john.smith@etoro.com
        calendarUrl:
          type: string
          nullable: true
          description: Calendar booking URL for scheduling meetings
          example: https://calendly.com/etoro-club
        avatars:
          type: array
          description: Manager avatar images in different sizes
          items:
            $ref: '#/components/schemas/ClubsApi_Avatar'
    ClubOffer:
      type: object
      description: A club benefit offer
      properties:
        id:
          type: string
          description: Offer identifier
          example: '80'
        displayName:
          type: string
          description: Offer display name
          example: Tax Return Offer
        description:
          type: string
          nullable: true
          description: Detailed offer description
          example: >-
            Discounted assistance with preparing annual tax returns from
            certified tax companies in your country.
        status:
          type: string
          enum:
            - Pending
            - Available
            - Reserved
            - Claimed
            - Expired
            - Claim Cancelled
            - Inventory Order Cancelled
          description: Offer status
          example: Claimed
        type:
          type: string
          enum:
            - Entertainment
            - Gifts
            - News
            - Signals
            - Tools
            - Exclusive events
            - Tickets
            - Zoom meetings
            - Educational
            - Services
            - Association Membership
            - Financial
            - Travel
            - Gift card
            - Client meetup
            - Emotional
            - Bundle
          description: Offer type
          example: Financial
        subType:
          type: string
          nullable: true
          enum:
            - High
            - Low
          description: Offer sub-type
        deliveryMethod:
          type: string
          nullable: true
          enum:
            - Inventory Managed
            - On-demand
            - Static
            - API
          description: Delivery method
          example: Static
        minimumClubLevel:
          type: string
          enum:
            - Internal
            - Bronze
            - Silver
            - Gold
            - Platinum
            - PlatinumPlus
            - Diamond
          description: Minimum club tier required for this offer
          example: Silver
        offerUrl:
          type: string
          nullable: true
          description: URL with more information about the offer
          example: https://www.etoro.com/club/offers/80
        offersInBundle:
          type: array
          nullable: true
          description: Offers bundled together with this offer
          items:
            $ref: '#/components/schemas/OfferInBundle'
        subOffers:
          type: array
          nullable: true
          description: Sub-offers within this offer
          items:
            $ref: '#/components/schemas/ClubOffer'
    StaticEligibleOffer:
      type: object
      description: An offer eligible across specific club tiers
      properties:
        id:
          type: string
          description: Offer identifier
          example: '80'
        displayName:
          type: string
          description: Offer display name
          example: Tax Return Offer
        description:
          type: string
          nullable: true
          description: Detailed offer description
          example: >-
            Discounted assistance with preparing annual tax returns from
            certified tax companies in your country.
        status:
          type: string
          enum:
            - Pending
            - Available
            - Reserved
            - Claimed
            - Expired
            - Claim Cancelled
            - Inventory Order Cancelled
          description: Offer status
          example: Claimed
        type:
          type: string
          enum:
            - Entertainment
            - Gifts
            - News
            - Signals
            - Tools
            - Exclusive events
            - Tickets
            - Zoom meetings
            - Educational
            - Services
            - Association Membership
            - Financial
            - Travel
            - Gift card
            - Client meetup
            - Emotional
            - Bundle
          description: Offer type
          example: Financial
        deliveryMethod:
          type: string
          nullable: true
          enum:
            - Inventory Managed
            - On-demand
            - Static
            - API
          description: Delivery method
          example: Static
        eligibleClubLevels:
          type: array
          description: Club tier names eligible for this offer
          items:
            type: string
            enum:
              - Internal
              - Bronze
              - Silver
              - Gold
              - Platinum
              - PlatinumPlus
              - Diamond
          example:
            - Gold
            - Silver
            - Platinum
            - PlatinumPlus
            - Diamond
    Webinar:
      type: object
      description: A club webinar event
      properties:
        id:
          type: integer
          format: int64
          description: Webinar identifier
          example: 83618564462
        topic:
          type: string
          description: Webinar topic
          example: Club Webinars with Lale Akoner and Sam North
        startTime:
          type: string
          format: date-time
          description: Scheduled start time in UTC
          example: '2026-05-20T14:00:00Z'
        joinUrl:
          type: string
          nullable: true
          description: URL to join the webinar (upcoming webinars only)
          example: https://us02web.zoom.us/j/83618564462
        recordUrl:
          type: string
          nullable: true
          description: URL to the recording (past webinars only)
          example: https://us02web.zoom.us/rec/play/example
    ClubsApi_Avatar:
      type: object
      description: Avatar image in a specific size
      properties:
        url:
          type: string
          description: Image URL
          example: >-
            https://openbook-static-files.s3.amazonaws.com/images/avatoros/50x50/af.png
        width:
          type: integer
          description: Image width in pixels
          example: 50
        height:
          type: integer
          description: Image height in pixels
          example: 50
    OfferInBundle:
      type: object
      description: An offer included in a bundle
      properties:
        type:
          type: string
          enum:
            - Entertainment
            - Gifts
            - News
            - Signals
            - Tools
            - Exclusive events
            - Tickets
            - Zoom meetings
            - Educational
            - Services
            - Association Membership
            - Financial
            - Travel
            - Gift card
            - Client meetup
            - Emotional
            - Bundle
          description: Bundle offer type
          example: Services
        offerLimit:
          type: integer
          description: Maximum number of offers in this bundle
          example: 3
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