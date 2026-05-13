### Live Orders Copy Location

This endpoint requires a pre-flight request.  
 Orders is the list of live orders (cancelled, filled, submitted).

To retrieve order information for a specific account, clients must first query the [/iserver/account endpoint](/campus/ibkr-api-page/cpapi-v1/#switch-account) to switch to the appropriate account.

Please be aware that filtering orders using the /iserver/account/orders endpoint will prevent order details from coming through over the [websocket “sor” topic](/campus/ibkr-api-page/cpapi-v1/#ws-order-updates-sub). To resolve this issue, developers should set “force=true” in a follow-up /iserver/account/orders call to clear any cached behavior surrounding the endpoint prior to calling for the websocket request.

`GET /iserver/account/orders`

#### Request Object

###### Query Params

**filters:** String.  
 Optionally filter your list of orders by a unique status value. More than one filter can be passed, separated by commas.

**force:** bool.  
 Force the system to clear saved information and make a fresh request for orders. Submission will appear as a blank array.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/orders?filters=filled&force=true"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/account/orders?filters=filled&force=true \
--request GET
```

#### Response Object

**NOTE:**: The /iserver/account/orders endpoint can contain a maximum of 1000 orders.

**orders:** Array of objects.  
 Contains all orders placed on the account for the day.  
 [{  
 **acct:** String.  
 Returns the accountID for the submitted order.

**conidex:** String.  
 Returns the contract identifier for the order.

**conid:** int.  
 Returns the contract identifier for the order.

**orderId:** int.  
 Returns the local order identifier of the order.

**cashCcy:** String.  
 Returns the currency used for the order.

**sizeAndFills:** String.  
 Returns the size of the order and how much of it has been filled.

**orderDesc:** String.  
 Returns the description of the order including the side, size, order type, price, and tif.

**description1:** String.  
 Returns the local symbol of the order.

**ticker:** String.  
 Returns the ticker symbol for the order.

**secType:** String.  
 Returns the security type for the order.

**listingExchange:** String.  
 Returns the primary listing exchange of the orer.

**remainingQuantity:** float.  
 Returns the remaining size for the order to fill.

**filledQuantity:** float.  
 Returns the size of the order already filled.

**companyName:** String.  
 Returns the company long name.

**status:** String.  
 Returns the current status of the order.

**order\_ccp\_status:** String.  
 Returns the current status of the order.

**origOrderType:** String.  
 Returns the original order type of the order, whether or not the type has been changed.

**supportsTaxOpt:** String.  
 Returns if the order is supported by the Tax Optimizer.

**lastExecutionTime:** String.  
 Returns the datetime of the order’s most recent execution.  
 Time returned is based on UTC timezone.  
 Value Format: YYMMDDHHmmss

**orderType:** String.  
 Returns the current order type, or the order at the time of execution.

**bgColor:** String.  
 Internal use only.

**fgColor:** String.  
 Internal use only.

**order\_ref:** String.  
 User defined string used to identify the order. Value is set using “cOID” field while placing an order.

**timeInForce:** String.  
 Returns the time in force (tif) of the order.

**lastExecutionTime\_r:** int.  
 Returns the epoch time of the most recent execution on the order.

**side:** String.  
 Returns the side of the order.

**avgPrice:** String.  
 Returns the average price of execution for the order.  
 }]

**snapshot:** bool.  
 Returns if the data is a snapshot of the account’s orders.

```
{
  "orders": [
    {
      "acct": "U1234567",
      "conidex": "265598",
      "conid": 265598,
      "account": "U1234567",
      "orderId": 1234568790,
      "cashCcy": "USD",
      "sizeAndFills": "5",
      "orderDesc": "Sold 5 Market, GTC",
      "description1": "AAPL",
      "ticker": "AAPL",
      "secType": "STK",
      "listingExchange": "NASDAQ.NMS",
      "remainingQuantity": 0.0,
      "filledQuantity": 5.0,
      "totalSize": 5.0,
      "companyName": "APPLE INC",
      "status": "Filled",
      "order_ccp_status": "Filled",
      "avgPrice": "192.26",
      "origOrderType": "MARKET",
      "supportsTaxOpt": "1",
      "lastExecutionTime": "231211180049",
      "orderType": "Market",
      "bgColor": "#FFFFFF",
      "fgColor": "#000000",
      "order_ref": "Order123",
      "timeInForce": "GTC",
      "lastExecutionTime_r": 1702317649000,
      "side": "SELL"
    }
  ],
  "snapshot": true
}
```
