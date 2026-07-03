> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Close position by units

> **Rate limit:** 20 requests per 60 seconds. This is a **shared quota** — the same budget is consumed by a group of related endpoints, so calling any of them reduces what is left for the others (you cannot call each at the full rate independently). Endpoints sharing this quota:
- `DELETE /api/v1/trading/execution/limit-orders/{orderId}`
- `DELETE /api/v1/trading/execution/market-close-orders/{orderId}`
- `DELETE /api/v1/trading/execution/market-open-orders/{orderId}`
- `DELETE /api/v2/trading/execution/orders/{orderId}`
- `POST /api/v1/trading/execution/limit-orders`
- `POST /api/v1/trading/execution/market-open-orders/by-amount`
- `POST /api/v1/trading/execution/market-open-orders/by-units`
- `POST /api/v2/trading/execution/orders`

---

This endpoint allows traders to close an entire position or a portion of it at the current market rate. If `UnitsToDeduct` is provided, only the specified portion will be closed. If `UnitsToDeduct` is omitted or set to null, the full position will be closed.



## OpenAPI

````yaml /api-reference/openapi.json post /api/v1/trading/execution/market-close-orders/positions/{positionId}
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
  /api/v1/trading/execution/market-close-orders/positions/{positionId}:
    post:
      tags:
        - Trading Real
      summary: Close position by units
      description: >-
        **Rate limit:** 20 requests per 60 seconds. This is a **shared quota** —
        the same budget is consumed by a group of related endpoints, so calling
        any of them reduces what is left for the others (you cannot call each at
        the full rate independently). Endpoints sharing this quota:

        - `DELETE /api/v1/trading/execution/limit-orders/{orderId}`

        - `DELETE /api/v1/trading/execution/market-close-orders/{orderId}`

        - `DELETE /api/v1/trading/execution/market-open-orders/{orderId}`

        - `DELETE /api/v2/trading/execution/orders/{orderId}`

        - `POST /api/v1/trading/execution/limit-orders`

        - `POST /api/v1/trading/execution/market-open-orders/by-amount`

        - `POST /api/v1/trading/execution/market-open-orders/by-units`

        - `POST /api/v2/trading/execution/orders`


        ---


        This endpoint allows traders to close an entire position or a portion of
        it at the current market rate. If `UnitsToDeduct` is provided, only the
        specified portion will be closed. If `UnitsToDeduct` is omitted or set
        to null, the full position will be closed.
      operationId: closePositionByMarketRate
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 3aebb03c-8e8f-42ff-a9f0-05aaf738585d
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
        - name: positionId
          in: path
          description: The unique identifier of the position to close.
          required: true
          schema:
            type: integer
            format: int64
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                InstrumentId:
                  type: integer
                  format: int32
                  description: >-
                    The ID of the financial instrument associated with the
                    position.
                UnitsToDeduct:
                  type: number
                  format: double
                  nullable: true
                  description: >-
                    The number of units to close. If omitted or null, the entire
                    position will be closed.
              required:
                - InstrumentId
      responses:
        '200':
          description: Successfully closed a position or a part of it.
          content:
            application/json:
              schema:
                type: object
                properties:
                  orderForClose:
                    type: object
                    properties:
                      positionID:
                        type: integer
                        description: The ID of the closed position.
                      instrumentID:
                        type: integer
                        description: The ID of the instrument traded.
                      unitsToDeduct:
                        type: number
                        format: double
                        description: The number of units closed in this order.
                      orderID:
                        type: integer
                        description: The unique identifier of the closing order.
                      orderType:
                        type: integer
                        description: The type of order executed.
                      statusID:
                        type: integer
                        description: The status of the closing order.
                      CID:
                        type: integer
                        description: Customer Account ID associated with the order.
                      openDateTime:
                        type: string
                        format: date-time
                        description: The timestamp when the order was placed.
                      lastUpdate:
                        type: string
                        format: date-time
                        description: The timestamp of the last update to this order.
                  token:
                    type: string
                    format: uuid
                    description: A unique confirmation token for the closing order.
              example:
                orderForClose:
                  positionID: 2150941015
                  instrumentID: 1111
                  unitsToDeduct: 2
                  orderID: 13904638
                  orderType: 19
                  statusID: 1
                  CID: 7765437
                  openDateTime: '2025-04-02T16:07:54.0880338Z'
                  lastUpdate: '2025-04-02T16:07:54.0880338Z'
                token: 5fe065bc-f6f9-4897-a2ce-c4fccef73ff8
          headers:
            RateLimit-Limit:
              description: >-
                Maximum number of requests allowed per window. This budget is
                SHARED across 9 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
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
                SHARED across 9 endpoints (it is NOT per-endpoint): a request to
                any endpoint in the group spends the same budget. See this
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
            - etoro-public:real:write
        - oauth2:
            - etoro-public:trade.real:write
components:
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