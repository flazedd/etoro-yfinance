### Modify Order Copy Location

Modifies an open order.

Must call /iserver/accounts endpoint prior to modifying an order.

Use /iservers/account/orders endpoint to review open-order(s).

`POST /iserver/account/{accountId}/order/{orderId}`

#### Request Object

###### Path Param

**accountId:** String.  
 The account ID for which account should place the order.

**orderId:** String.  
 The orderID for that should be modified.  
 Can be retrieved from /iserver/account/orders

###### Body Params

The body content of the modify order endpoint will follow the same structure as the standard /iserver/account/{accountId}/orders endpoint.

The content should mirror the content of the original order.

**manualIndicator:** boolean. Required\*  
 **IMPORTANT** This field is required when trading Futures and Futures Options contracts to remain in compliance with [CME Group Rule 536-B](https://www.cmegroup.com/rulebook/files/cme-group-Rule-536-B-Tag1028.pdf).  
 The Manual Order Indicator is used to determine if an order was modified manually or through an automated tool. Regardless of original submission, the modification must also include the manualIndicator tag to signify of the order modification was manual or automated.  
 true indicates the order was modified manually through an interface while false indicates an order was modified through an automated system.

**extOperator:** string. Required\*  
 **IMPORTANT** This field is required when trading Futures and Futures Options contracts to remain in compliance with [CME Group Rule 536-B](https://www.cmegroup.com/rulebook/files/cme-group-Rule-536-B-Tag1028.pdf).  
 The External Operator field should contain information regarding the submitting user in charge of the API operation at the time of request submission.

See the [Place Order](/campus/ibkr-api-page/cpapi-v1/#place-order) section for more details.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/U1234567/order/123456789
json_content = {
  "conid": 265598,
  "orderType": "STP",
  "price": 180,
  "side": "BUY",
  "tif": "DAY",
  "quantity": 10,
  "manualIndicator":True,
  "extOperator": "person1234"
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account/U1234567/order/123456789 \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "conid": 265598,
  "orderType": "STP",
  "price": 180,
  "side": "BUY",
  "tif": "DAY",
  "quantity": 10,
  "manualIndicator":true,
  "extOperator": "person1234"

}'
```

#### Response Object

**orderId:** String.  
 Returns the orders identifier which can be used for order tracking, modification, and cancellation.

**order\_status:** String.  
 Returns the order status of the current market order.  
 See [Order Status Value](/campus/ibkr-api-page/cpapi-v1/#order-status-value) for more information.

**encrypt\_message:** String.  
 Returns a “1” to display that the message sent was encrypted.

```
[
    {
        "order_id": "1234567890",
        "order_status": "Submitted",
        "encrypt_message": "1"
    }
]
```

#### Alternate Response Object

In some instances, you will receive an ID along with a message about your order.

See the [Place Order Reply](/campus/ibkr-api-page/cpapi-v1/#place-order-reply) section for more details on resolving the confirmation.

**id:** String.  
 Returns a message ID relating to the particular order’s warning confirmation.

**message:** Array of Strings.  
 Returns the message warning about why the order wasn’t initially transmitted.

**isSuppressed:** bool.  
 Returns if a particular warning was suppressed before sending.  
 Always returns false.

**messageIds:** Array of Strings.  
 Returns an internal message identifier (Internal use only).

```
[
  {
    "id": "a12b34c5-d678-9e012f-3456-7a890b12cd3e",
    "message": [
      "You are about to submit a stop order. Please be aware of the various stop order types available and the risks associated with each one.\nAre you sure you want to submit this order?"
    ],
    "isSuppressed": false,
    "messageIds": [
      "o0"
    ]
  }
]
```
