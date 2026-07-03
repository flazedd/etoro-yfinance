> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create a price alert

> **Rate limit:** 60 requests per 60 seconds. This is the **default shared quota** — it is shared with every other endpoint that has no dedicated limit, so requests across those endpoints all draw from the same budget.

---

Creates a new price alert for the authenticated user. The alert will fire when the market bid price reaches the target price. Provide a symbol to identify the instrument.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/price-alerts
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
  /api/v1/price-alerts:
    post:
      tags:
        - Price Alerts
      summary: Create a price alert
      description: >-
        **Rate limit:** 60 requests per 60 seconds. This is the **default shared
        quota** — it is shared with every other endpoint that has no dedicated
        limit, so requests across those endpoints all draw from the same budget.


        ---


        Creates a new price alert for the authenticated user. The alert will
        fire when the market bid price reaches the target price. Provide a
        symbol to identify the instrument.
      operationId: postPriceAlerts
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: c732baee-6a17-4f69-ae26-d4725848627b
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
              $ref: '#/components/schemas/CreatePriceAlertRequest'
            example:
              symbol: AAPL
              targetPrice: 185.5
      responses:
        '201':
          description: Price alert created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertMutationResponse'
              example:
                success: true
                data:
                  alertId: a1b2c3d4-e5f6-7890-abcd-ef1234567890
                  instrumentId: 1001
                  symbol: AAPL
                  targetPrice: 185.5
                  currentPrice: 182.3
                  createdAt: '2026-04-30T10:00:00Z'
                  updatedAt: '2026-04-30T10:00:00Z'
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
            Invalid request parameters (e.g. missing symbol, invalid
            targetPrice)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertErrorResponse'
              example:
                success: false
                error:
                  code: INVALID_PARAMETER
                  message: Invalid request parameters
                  details: Field 'targetPrice' must be greater than 0
                  field: targetPrice
        '401':
          description: Unauthorized - missing or invalid authentication credentials
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertsApi_PublicErrorResponse'
              example:
                errorCode: Unauthorized
                errorMessage: Unauthorized
        '403':
          description: Forbidden - insufficient permissions
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertsApi_PublicErrorResponse'
              example:
                errorCode: InsufficientPermissions
                errorMessage: Insufficient permissions to access this resource
        '404':
          description: Instrument not found for the provided symbol
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertErrorResponse'
              example:
                success: false
                error:
                  code: INSTRUMENT_NOT_FOUND
                  message: Instrument not found
                  details: No instrument found for symbol 'INVALID'
        '422':
          description: Business rule violation (e.g. duplicate alert, max alerts exceeded)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertErrorResponse'
              example:
                success: false
                error:
                  code: MAX_ALERTS_EXCEEDED
                  message: Maximum number of alerts reached
                  details: You have reached the maximum number of active price alerts
        '429':
          description: Too many requests
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertsApi_PublicErrorResponse'
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
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PriceAlertsApi_PublicErrorResponse'
              example:
                errorCode: UnhandledException
                errorMessage: Global Error
      security:
        - oauth2:
            - etoro-public:price-alerts:write
components:
  schemas:
    CreatePriceAlertRequest:
      type: object
      description: Request body for creating a new price alert
      required:
        - symbol
        - targetPrice
      properties:
        symbol:
          type: string
          description: Trading symbol to identify the instrument (e.g. AAPL, TSLA)
          example: AAPL
        targetPrice:
          type: number
          format: decimal
          description: >-
            Target price at which the alert should trigger. Must be greater than
            0.
          exclusiveMinimum: true
          example: 185.5
          minimum: 0
    PriceAlertMutationResponse:
      type: object
      description: Response for price alert create and update operations
      properties:
        success:
          type: boolean
          description: Indicates the operation completed successfully
          example: true
        data:
          $ref: '#/components/schemas/PriceAlert'
    PriceAlertErrorResponse:
      type: object
      description: Error response from the price alerts service
      required:
        - success
        - error
      properties:
        success:
          type: boolean
          description: Indicates the request failed
          example: false
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: Machine-readable error code for programmatic handling
              example: VALIDATION_ERROR
            message:
              type: string
              description: Human-readable error message
              example: Invalid request parameters
            details:
              type: string
              description: Additional context about the error
              example: Field 'targetPrice' must be greater than 0
            field:
              type: string
              description: The specific field that caused the error (if applicable)
              example: targetPrice
    PriceAlertsApi_PublicErrorResponse:
      type: object
      description: Standard error response from the public API gateway
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
    PriceAlert:
      type: object
      description: A price alert set by the user on a financial instrument
      required:
        - alertId
        - instrumentId
        - symbol
        - targetPrice
        - currentPrice
        - createdAt
        - updatedAt
      properties:
        alertId:
          type: string
          format: uuid
          description: Unique identifier of the price alert
          example: a1b2c3d4-e5f6-7890-abcd-ef1234567890
        instrumentId:
          type: integer
          description: Unique instrument identifier used across all trading operations
          example: 1001
        symbol:
          type: string
          description: Trading symbol displayed to users (e.g. AAPL, TSLA)
          example: AAPL
        targetPrice:
          type: number
          format: decimal
          description: Target price at which the alert will trigger
          example: 185.5
        currentPrice:
          type: number
          format: decimal
          description: Market bid price at the time the alert was created or last updated
          example: 182.3
        createdAt:
          type: string
          format: date-time
          description: Timestamp when the alert was created (ISO 8601 UTC)
          example: '2026-04-20T10:00:00Z'
        updatedAt:
          type: string
          format: date-time
          description: Timestamp when the alert was last updated (ISO 8601 UTC)
          example: '2026-04-25T14:30:00Z'
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