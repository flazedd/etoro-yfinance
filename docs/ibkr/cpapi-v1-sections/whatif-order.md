### Preview Order / WhatIf Order Copy Location

This endpoint allows you to preview order without actually submitting the order and you can get commission information in the response. Also supports bracket orders.

**Note:** Please be aware that /whatif orders are also effected by our [message suppression endpoint](/campus/ibkr-api-page/cpapi-v1/#questions-suppress).

Clients must query [/iserver/marketdata/snapshot](/campus/ibkr-api-page/cpapi-v1/#md-snapshot) for the instrument prior to requesting the /whatif endpoint.

`POST /iserver/account/{accountId}/orders/whatif`

#### Request Object

The body content of the /whatif endpoint will follow the same structure as the standard /iserver/account/{accountId}/orders endpoint.

See the [Place Order](/campus/ibkr-api-page/cpapi-v1/#place-order) section for more details.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/U1234567/orders/whatif"
json_content = {
  "orders": [
    {
      "conid": 265598,
      "orderType": "LMT",
      "price": 200.25,
      "side": "BUY",
      "tif": "DAY",
      "quantity": 5
    }
  ]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account/U1234567/orders/whatif \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "orders": [
    {
      "conid": 265598,
      "orderType": "LMT",
      "price": 200.25,
      "side": "BUY",
      "tif": "DAY",
      "quantity": 5
    }
  ]
}'
```

#### Response Object

**amount:** Object.  
 Contains the details about the order cost.  
 {  
 **amount:** String.  
 Returns the cost of the base order.

**commission:** String.  
 Returns the commission cost of the base order.

**total:** String.  
 Returns the total cost of the order.  
 },

**equity:** Object.  
 Contains the details about the order’s impact on your equity.  
 {  
 **current:** String.  
 Returns the current equity of the account.

**change:** String.  
 Returns the equity impact from the order.

**after:** String.  
 Returns the equity after the order is traded.  
 },

**initial:** Object.  
 Contains the details about the order’s impact on your initial margin.  
 {  
 **current:** String.  
 Returns the current initial margin value.

**change:** String.  
 Returns the amount the initial margin will change by.

**after:** String.  
 Returns the initial margin value after the order.  
 },

**maintenance:** Object.  
 Contains the details about the order’s impact on your maintenance margin.  
 {  
 **current:** String.  
 Returns the current maintenance margin value.

**change:** String.  
 Returns the amount the maintenance margin will change by.

**after:** String.  
 Returns the maintenance margin value after the transaction.  
 },

**position:** Object.  
 Contains the details about the order’s impact on your current position.  
 {  
 **current:** String.  
 Returns the cost of the base order.

**change:** String.  
 Returns the cost of the base order.

**after:** String.  
 Returns the cost of the base order.  
 },

**warn:** String.  
 Returns any potential warning message from placing this order.  
 Returns null if no warning is possible.

**error:** String.  
 Returns any potential error message from placing this order.  
 Returns null if no error is possible.

```
{
  "amount": {
    "amount": "1,977.60 USD (10 Shares)",
    "commission": "1 USD",
    "total": "1,978.60 USD"
  },
  "equity": {
    "current": "215,415,594",
    "change": "-1",
    "after": "215,415,593"
  },
  "initial": {
    "current": "116,965",
    "change": "652",
    "after": "117,617"
  },
  "maintenance": {
    "current": "106,332",
    "change": "592",
    "after": "106,924"
  },
  "position": {
    "current": "0",
    "change": "10",
    "after": "10"
  },
  "warn": "21/You are trying to submit an order without having market data for this instrument. \nIB strongly recommends against this kind of blind trading which may result in \nerroneous or unexpected trades.",
  "error": null
}
```
