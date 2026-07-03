> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get user profile and account summary

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Returns detailed user profile information including account status, verification levels, biographical data, and associated metadata. This endpoint aggregates essential user information from multiple sources to provide a complete user profile overview.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/user-info/people
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
  /api/v1/user-info/people:
    get:
      tags:
        - Users Info
      summary: Get user profile and account summary
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Returns detailed user profile information including account status,
        verification levels, biographical data, and associated metadata. This
        endpoint aggregates essential user information from multiple sources to
        provide a complete user profile overview.
      operationId: getUserInfoPeople
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 70155cb2-1b9f-4f59-88a6-fef4cfd46663
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
        - name: usernames
          in: query
          schema:
            type: array
            items:
              type: string
          explode: false
          required: false
        - name: cidList
          in: query
          schema:
            type: array
            items:
              type: integer
          explode: false
          required: false
      responses:
        '200':
          description: Successfully retrieved user information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PublicAggregatedInfoResponse'
              example:
                users:
                  - gcid: 1536861
                    realCID: 1563191
                    demoCID: 1563191
                    username: exampleuser
                    language: 1
                    languageIsoCode: en-GB
                    country: 54
                    allowDisplayFullName: false
                    userBio:
                      gcid: 1536861
                      languageCode: null
                    whiteLabel: 1
                    optOut: true
                    homepage: null
                    playerStatus: null
                    piLevel: 0
                    isPi: false
                    avatars:
                      - url: >-
                          https://***.s3.amazonaws.com/images/avatoros/35x35/cy.png
                        width: 35
                        height: 35
                        type: Resized
                      - url: >-
                          https://***.s3.amazonaws.com/images/avatoros/50x50/cy.png
                        width: 50
                        height: 50
                        type: Resized
                      - url: >-
                          https://***.s3.amazonaws.com/images/avatoros/150x150/cy.png
                        width: 150
                        height: 150
                        type: Resized
                    masterAccountCid: null
                    accountType: 1
                    fundType: null
                    isVerified: false
                    verificationLevel: 1
                    accountStatus: 1
                    gdprInfo: null
                    userFlowSignature: >-
                      233a065f3f8d7e344516fc75f7e6c4646a0c0d38798c00e4655fa0a9447ea223
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
          description: >-
            Invalid request - Typically due to exceeding maximum usernames limit
            or invalid username format
        '404':
          description: One or more requested usernames not found
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
    PublicAggregatedInfoResponse:
      type: object
      description: Container for the aggregated user information response
      properties:
        users:
          type: array
          description: Array of user profiles with their associated information
          items:
            $ref: '#/components/schemas/PublicAggregatedInfoUser'
    PublicAggregatedInfoUser:
      type: object
      description: >-
        Comprehensive user profile information including account details,
        verification status, and preferences
      properties:
        gcid:
          type: integer
          description: Global Customer ID - Unique identifier across all systems
        realCID:
          type: integer
          description: Customer ID for real trading account
        demoCID:
          type: integer
          nullable: true
          description: Customer ID for demo/practice account if available
        username:
          type: string
          description: Unique username identifier for the user
        language:
          type: integer
          nullable: true
          description: User's preferred language ID based on system language codes
        languageIsoCode:
          type: string
          description: ISO 639-1 language code for user's preferred language
        country:
          type: integer
          nullable: true
          description: User's registered country ID based on system country codes
        allowDisplayFullName:
          type: boolean
          description: >-
            Indicates whether the user has consented to displaying their full
            name publicly
        userBio:
          $ref: '#/components/schemas/PublicAggregatedInfoUiUserBio'
          description: Structured biographical information including trading strategy
        whiteLabel:
          type: integer
          nullable: true
          description: White label partner identifier if user belongs to a partner program
        optOut:
          type: boolean
          description: Indicates if user has opted out of public profile features
        homepage:
          type: integer
          nullable: true
        playerStatus:
          type: integer
          nullable: true
        piLevel:
          type: integer
          nullable: true
        isPi:
          type: boolean
          description: Indicates if user is a Professional Investor with special privileges
        avatars:
          type: array
          items:
            $ref: '#/components/schemas/PublicAggregatedInfoUiUserAvatar'
        masterAccountCid:
          type: integer
          nullable: true
        accountType:
          type: integer
          nullable: true
        fundType:
          type: string
          nullable: true
        isVerified:
          type: boolean
        verificationLevel:
          type: integer
          description: User's current verification level (0-3, where 3 is fully verified)
        accountStatus:
          type: integer
          nullable: true
          description: >-
            Current account status code indicating active, suspended, or other
            states
        gdprInfo:
          type: object
          nullable: true
          properties:
            accountStatus:
              $ref: '#/components/schemas/PublicAggregatedInfoAccountStatus'
            playerStatus:
              $ref: '#/components/schemas/PublicAggregatedInfoPlayerStatus'
            playerStatusReason:
              $ref: '#/components/schemas/PublicAggregatedInfoPlayerStatusReason'
        firstName:
          type: string
          nullable: true
          description: User's first name (visible if allowDisplayFullName is true)
        middleName:
          type: string
          nullable: true
          description: User's middle name
        lastName:
          type: string
          nullable: true
          description: User's last name (visible if allowDisplayFullName is true)
        aboutMe:
          type: string
          nullable: true
          description: User's full about me text
        aboutMeShort:
          type: string
          nullable: true
          description: Short summary of user's about me text
        customerRestrictions:
          type: array
          nullable: true
          items:
            type: object
            properties:
              CID:
                type: integer
                description: Customer ID
              restrictionTypeID:
                type: integer
                description: Type of restriction
              reasonID:
                type: integer
                description: Reason for restriction
              occured:
                type: string
                format: date-time
                description: When the restriction occurred
          description: List of customer restrictions applied to the account
        userFlowSignature:
          type: string
    PublicAggregatedInfoUiUserBio:
      type: object
      properties:
        gcid:
          type: integer
        languageCode:
          type: string
          nullable: true
        aboutMe:
          type: string
          nullable: true
          description: User's full about me text
        aboutMeShort:
          type: string
          nullable: true
          description: Short summary of user's about me text
        strategyID:
          type: integer
          nullable: true
          description: ID of the user's trading strategy
    PublicAggregatedInfoUiUserAvatar:
      type: object
      properties:
        url:
          type: string
        width:
          type: integer
        height:
          type: integer
        type:
          type: string
          enum:
            - Original
            - OriginalCropped
            - Resized
            - Retouched
          description: Type of avatar image
    PublicAggregatedInfoAccountStatus:
      type: integer
      enum:
        - 1
        - 2
      x-enumNames:
        - Open
        - Closed
      nullable: true
    PublicAggregatedInfoPlayerStatus:
      type: integer
      enum:
        - 1
        - 2
        - 3
        - 4
        - 5
        - 6
        - 7
        - 8
        - 9
        - 10
        - 11
        - 12
        - 13
        - 14
        - 15
      x-enumNames:
        - Normal
        - Blocked
        - ChatBlocked
        - BlockedUponRequest
        - Warning
        - BlockedUnderInvestigation
        - ScalpersBlock
        - BlockedPayPalInvestigation
        - TradeBlock
        - DepositBlocked
        - SocialIndex
        - CopyBlock
        - PendingVerification
        - BlockedFailedVerification
        - BlockTrading
      nullable: true
    PublicAggregatedInfoPlayerStatusReason:
      type: integer
      enum:
        - 0
        - 1
        - 2
        - 3
        - 4
        - 5
        - 6
        - 7
        - 8
        - 9
        - 10
        - 11
        - 12
        - 13
        - 14
        - 15
        - 16
        - 17
        - 18
        - 19
        - 20
        - 21
        - 22
        - 23
        - 24
        - 25
        - 26
        - 27
        - 28
        - 29
        - 30
        - 31
        - 32
        - 33
        - 34
        - 35
        - 36
        - 37
        - 38
        - 39
        - 40
        - 41
        - 42
      x-enumNames:
        - None
        - FailedVerification
        - ExpiredDocument
        - CloseAccountByUser
        - Risk
        - Chargeback
        - AMLAccountClosed
        - HRC
        - Underage
        - Deceased
        - AML
        - AMLreview
        - OffMarketAbuse
        - Overpayment
        - RiskCheck
        - ThirdParty
        - PayPalInvestigation
        - NOC_NOF_RFI
        - WCHMatch
        - Other
        - RightToBeForgotten
        - SelfService
        - ByRequest
        - ACHChargeback
        - PWMBChargeback
        - Abuse
        - AffiliateAccount
        - PendingDocs
        - EmployeeAccount
        - PIAccount
        - CheckoutChargeback
        - CheckoutRetrievel
        - CheckoutCaptureDecline
        - EToroMoneyRestriction
        - AbusiveTrading
        - HackedAccount
        - PartnersAndPIs
        - CS_ManagementDecision
        - Deposits
        - KYC
        - AccountClosed
        - Tax
        - Corporate
      nullable: true
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