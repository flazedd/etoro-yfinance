> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Upload a media attachment

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Two-step media upload: clients first upload a file here to receive an Attachment object, then pass its url in a POST /feeds/post or POST /reactions/.../comment payload. Accepts multipart/form-data with a binary file field. Supported formats: JPEG and PNG. Maximum file size: 8 MB (8,388,608 bytes). The returned url is a plain CDN URL scoped to the uploading user.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/attachments
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
  /api/v1/attachments:
    post:
      tags:
        - Social Feeds
      summary: Upload a media attachment
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Two-step media upload: clients first upload a file here to receive an
        Attachment object, then pass its url in a POST /feeds/post or POST
        /reactions/.../comment payload. Accepts multipart/form-data with a
        binary file field. Supported formats: JPEG and PNG. Maximum file size: 8
        MB (8,388,608 bytes). The returned url is a plain CDN URL scoped to the
        uploading user.
      operationId: postAttachments
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 92c71cb3-ba3d-4287-91c8-6a9b4f2fb0df
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
        - name: client_request_id
          in: query
          required: true
          description: >-
            Client-generated correlation ID (UUID). Required for request tracing
            and idempotency.
          schema:
            type: string
            format: uuid
          example: dcbf75de-be53-47fe-bfd0-61365e74f9d4
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required:
                - file
              properties:
                file:
                  type: string
                  format: binary
                  description: >-
                    Required. The image file to upload. Supported formats: JPEG
                    and PNG. Maximum size: 8 MB (8,388,608 bytes), enforced
                    server-side.
            encoding:
              file:
                contentType: image/jpeg, image/png
      responses:
        '200':
          description: Attachment uploaded successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Attachment'
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
          description: Bad request — missing file or URL
        '401':
          description: Authentication required
        '422':
          description: Unsupported file type or file exceeds 8 MB limit
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