> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get Order Information and Position Details for Real Account

> Deprecated: This endpoint is no longer present in the current eToro Public API Swagger. Prefer the current replacement endpoints where available.

Retrieves comprehensive information about a specific order for opening a position, including the order status, execution details, and all positions that were opened from this order. This endpoint is essential for tracking order execution and identifying which positions were created as a result of a specific order request. The response includes detailed position information with PositionID values that can be used to query position-specific details.



## OpenAPI

````yaml /api-reference/openapi.json get /api/v1/trading/info/real/orders/{orderId}
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
  /api/v1/trading/info/real/orders/{orderId}:
    get:
      tags:
        - Deprecated
      summary: Get Order Information and Position Details for Real Account
      description: >-
        Deprecated: This endpoint is no longer present in the current eToro
        Public API Swagger. Prefer the current replacement endpoints where
        available.


        Retrieves comprehensive information about a specific order for opening a
        position, including the order status, execution details, and all
        positions that were opened from this order. This endpoint is essential
        for tracking order execution and identifying which positions were
        created as a result of a specific order request. The response includes
        detailed position information with PositionID values that can be used to
        query position-specific details.
      operationId: getRealOrderForOpenInfo
      parameters:
        - name: x-request-id
          in: header
          required: true
          schema:
            type: string
            format: uuid
            example: 67a6927c-4349-40a3-9c31-c98b26f4b863
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
          description: >-
            The unique identifier of the order for opening a position. This is
            the OrderID that was returned when the order was initially created.
          schema:
            type: integer
            format: int64
          example: 123456789
      responses:
        '200':
          description: >-
            Successfully retrieved order information and associated position
            details.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderForOpenInfoResponse'
              example:
                token: 550e8400-e29b-41d4-a716-446655440000
                orderID: 123456789
                cid: 987654321
                statusID: 1
                orderType: 1
                openActionType: 1
                errorCode: null
                errorMessage: null
                instrumentID: 67890
                amount: 1000
                units: 10.5
                requestOccurred: '2024-01-15T10:30:00Z'
                positions:
                  - positionID: 9876543210
                    orderType: 1
                    occurred: '2024-01-15T10:30:15Z'
                    rate: 1.2345
                    units: 10.5
                    conversionRate: 1
                    amount: 1000
                    isOpen: true
        '400':
          description: Bad Request - Invalid orderId format, or validation error occurred.
        '404':
          description: >-
            Not Found - The specified order was not found for the provided
            OrderID.
        '500':
          description: >-
            Internal Server Error - An unexpected error occurred while
            processing the request.
      deprecated: true
      security:
        - bearerAuth: []
components:
  schemas:
    OrderForOpenInfoResponse:
      type: object
      description: >-
        Comprehensive order information response containing order details and
        all positions opened from this order.
      required:
        - orderID
        - CID
        - statusID
        - orderType
        - instrumentID
        - requestOccurred
      properties:
        token:
          type: string
          description: >-
            Tracking token for the request, used for correlation and debugging
            purposes. This token is generated by the system and can be used to
            track the request through various system components.
          example: 550e8400-e29b-41d4-a716-446655440000
        orderID:
          type: integer
          format: int64
          description: >-
            The unique identifier of the order. This is the same OrderID that
            was provided in the request path parameter.
          example: 123456789
        CID:
          type: integer
          format: int64
          description: >-
            Customer ID (CID) associated with the order. This identifies the
            user account that created the order.
          example: 987654321
        referenceID:
          type: string
          description: Reference tracking ID for the order request.
          example: 00000000-0000-0000-0000-000000000000
        statusID:
          type: integer
          description: >-
            Current status of the order. Common values: 0 = Pending, 1 =
            Executed, 2 = Cancelled, 3 = Rejected, 4 = Partially Executed. The
            exact meaning of status codes may vary based on order type and
            system configuration.
          example: 1
        orderType:
          type: integer
          description: >-
            Type of the order. Common values: 1 = Market Order, 2 = Limit Order,
            3 = Stop Order. The exact order types depend on the trading system
            configuration.
          example: 1
        openActionType:
          type: integer
          description: >-
            The action type that triggered the order creation. This indicates
            the reason or context for opening the position, such as manual
            trade, copy trading, automated strategy, etc.
          example: 1
        errorCode:
          type: integer
          format: nullable
          description: >-
            Error code if the order execution failed or encountered an error.
            This field is null if the order was successful. Error codes are
            system-specific and should be referenced against the system's error
            code documentation.
          example: null
        errorMessage:
          type: string
          format: nullable
          description: >-
            Human-readable error message describing any error that occurred
            during order processing. This field is null if the order was
            successful. Provides additional context beyond the errorCode.
          example: null
        instrumentID:
          type: integer
          description: >-
            The unique identifier of the financial instrument that the order was
            placed for. This corresponds to the instrument being traded (e.g.,
            stock, currency pair, commodity).
          example: 67890
        amount:
          type: number
          format: decimal
          description: >-
            The USD amount that was requested to be invested in the position.
            This represents the monetary value allocated to the order.
          example: 1000
        units:
          type: number
          format: decimal
          description: >-
            The number of units that were requested to be traded. If the order
            was placed by units rather than amount, this value represents the
            requested quantity.
          example: 10.5
        requestOccurred:
          type: string
          format: date-time
          description: >-
            The timestamp when the order request was initially created and
            submitted to the system. This is in ISO 8601 format (UTC).
          example: '2024-01-15T10:30:00Z'
        positions:
          type: array
          description: >-
            List of all positions that were opened as a result of this order.
            Each position in this array represents a successfully executed
            position created from the order. This array is empty if the order
            has not yet been executed or if execution failed.
          items:
            $ref: '#/components/schemas/OrderForOpenPositionInfo'
    OrderForOpenPositionInfo:
      type: object
      description: >-
        Detailed information about a position that was opened from an order.
        This object contains all the essential details needed to identify and
        track the position.
      required:
        - positionID
        - orderType
        - occurred
        - rate
        - units
        - amount
        - isOpen
      properties:
        positionID:
          type: integer
          format: int64
          description: >-
            The unique identifier of the position that was opened from this
            order. This PositionID is the key property that can be used to query
            detailed position information, track position status, and perform
            position-specific operations. This is the primary identifier for the
            position in the trading system.
          example: 9876543210
        orderType:
          type: integer
          description: >-
            The type of order that was used to open this position. This matches
            the orderType from the parent order and indicates the execution
            method (e.g., Market Order, Limit Order).
          example: 1
        occurred:
          type: string
          format: date-time
          description: >-
            The exact timestamp when this position was opened and executed. This
            is in ISO 8601 format (UTC) and represents when the position became
            active in the trading system.
          example: '2024-01-15T10:30:15Z'
        rate:
          type: number
          format: decimal
          description: >-
            The execution rate (price) at which the position was opened. This is
            the actual price at which the trade was executed, which may differ
            from the requested rate depending on market conditions and order
            type.
          example: 1.2345
        units:
          type: number
          format: decimal
          description: >-
            The number of units in the position. This represents the quantity of
            the instrument that was acquired when the position was opened.
          example: 10.5
        conversionRate:
          type: number
          format: decimal
          description: >-
            The currency conversion rate that was applied when opening the
            position. This rate is used to convert between the instrument's base
            currency and the account currency (typically USD) at the time of
            execution.
          example: 1
        amount:
          type: number
          format: decimal
          description: >-
            The USD amount that was invested in this position. This represents
            the monetary value allocated to this specific position.
          example: 1000
        isOpen:
          type: boolean
          description: >-
            Indicates whether the position is currently open (true) or has been
            closed (false). This status reflects the current state of the
            position at the time the order information was retrieved.
          example: true

````