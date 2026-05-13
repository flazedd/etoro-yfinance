### Place Order Reply Confirmation Copy Location

Confirm order precautions and warnings presented from placing orders. Orders **must** be replied to immediately after receiving the reply message. Submitting other orders or other requests will cancel the order and attempts to acknowledge the reply will result in a 503 error.

Users that wish to avoid receiving /reply message should consider using the [Suppression](/campus/ibkr-api-page/cpapi-v1/#questions-suppress) endpoint to automatically accept them.

```
POST /iserver/reply/{{ replyId }}
```

#### Request Object

###### Path Params

**replyId:** String. Required  
 Include the id value from the prior order request relating to the particular order’s warning confirmation.

###### Body Params

**confirmed:** bool. Required  
 Pass your confirmation to the reply to allow or cancel the order to go through.  
 true will agree to the message transmit the order.  
 false will decline the message and discard the order.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/reply/a12b34c5-d678-9e012f-3456-7a890b12cd3e"
json_content = {"confirmed":true}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/reply/a12b34c5-d678-9e012f-3456-7a890b12cd3e \
--request POST \
--header 'Content-Type:application/json' \
--data '{"confirmed":true}'
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

**NOTE:** After sending your initial confirmation to the /iserver/reply/{replyId} endpoint, you may receive additional reply messages. These confirmation messages must also be responded to before the order will submit.
