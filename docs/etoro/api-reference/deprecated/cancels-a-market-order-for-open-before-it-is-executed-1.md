> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Cancels a market order for open before it is executed.

> Deprecated: This endpoint is no longer present in the current eToro Public API Swagger. Prefer the current replacement endpoints where available.

This endpoint allows traders to cancel a market order for open before execution. If the order has already been processed, cancellation will not be possible.



## OpenAPI

````yaml /api-reference/openapi.json delete /api/v1/trading/execution/market-open-orders/{orderId}
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
  /api/v1/trading/execution/market-open-orders/{orderId}:
    delete:
      tags:
        - Deprecated
      summary: Cancels a market order for open before it is executed.
      description: >-
        Deprecated: This endpoint is no longer present in the current eToro
        Public API Swagger. Prefer the current replacement endpoints where
        available.


        This endpoint allows traders to cancel a market order for open before
        execution. If the order has already been processed, cancellation will
        not be possible.
      operationId: cancelOpenMarketOrder
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 99871678-c1cc-4c89-9a72-903e0e6529d1
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
        - name: orderId
          in: path
          required: true
          schema:
            type: integer
            format: int64
          description: The unique identifier of the market order for open to be canceled.
      responses:
        '200':
          description: >-
            Successfully canceled the pending market order. The response
            includes a confirmation token.
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                    format: uuid
                    description: A confirmation token indicating the order cancellation.
                required:
                  - token
              example:
                token: 9af05785-be29-482d-a892-9d9be4fd34bc
      deprecated: true

````