### Place Order Copy Location

When connected to an IServer Brokerage Session, this endpoint will allow you to submit orders.

CP WEB API supports various advanced orderTypes, for additional details and examples refer to the [Order Types](/campus/ibkr-api-page/order-types/) page.

**Cash Quantity:** Send orders using monetary value by specifying cashQty instead of quantity, e.g. cashQty: 200. The endpoint /iserver/contract/rules returns list of valid orderTypes in cqtTypes.  
 Note: See [Cash Quantity Orders in the Web API](/campus/ibkr-api-page/cpapi-v1/#cash-qty) for more details.

**Currency Conversion:** Convert cash from one currency to another by including isCcyConv = true. To specify the cash quantity use fxQTY instead of quantity, e.g. fxQTY: 100.

**IB Algos:** Attached user-defined settings to your trades by using any of IBKR’s Algo Orders. Use the endpoint /iserver/contract/{conid}/algos to identify the available strategies for a contract.

**Notes:**

- With the exception of OCA groups and bracket orders, the orders endpoint does not currently support the placement of unrelated orders in bulk.
- Developers should not attempt to place another order until the previous order has been fully acknowledged, that is, when no further warnings are received deferring the client to the reply endpoint.

```
POST /iserver/account/{accountID}/orders
```

#### Request Object

###### Path Params

**accountId:** String.  
 The account ID for which account should place the order.  
 Financial Advisors should instead specify their allocation group.

###### Body Params

**orders:** Array of Objects. Required  
 Used to the order content.  
 [{  
 **acctId:** String.  
 It should be one of the accounts returned by /iserver/accounts.  
 If not passed, the first one in the list is selected.

**conid:** int. Required\*  
 conid is the identifier of the security you want to trade.  
 Using the conid field will force the order to be SMART-routed, even if conidex is specified.  
 You can find the conid with /iserver/secdef/search.  
 \*Can use conidex instead of conid.

**conidex:** int. Required\*  
 conidex is the identifier for the security and exchange you want to trade.  
 Direct routed orders cannot use the conid field in addition to conidex, otherwise the order will be automatically routed to SMART.  
 You can find the conid and list of exchanges with /iserver/secdef/search.  
 \*Can use conidex instead of conid.

**manualIndicator:** boolean. Required\*  
 **IMPORTANT** This field is required when trading Futures and Futures Options contracts to remain in compliance with [CME Group Rule 536-B](https://www.cmegroup.com/rulebook/files/cme-group-Rule-536-B-Tag1028.pdf).  
 The Manual Order Indicator is used to determine if an order was manual entered or done through an automated tool.  
 true indicates the order was submitted manually through an interface while false indicates an order was submitted autonomously.

**extOperator:** string. Required\*  
 **IMPORTANT** This field is required when trading Futures and Futures Options contracts to remain in compliance with [CME Group Rule 536-B](https://www.cmegroup.com/rulebook/files/cme-group-Rule-536-B-Tag1028.pdf).  
 The External Operator field should contain information regarding the submitting user in charge of the API operation at the time of request submission.

**secType:** String.  
 The contract-identifier (conid) and security type (type) specified as a concatenated value  
 Value Format: “conid:type”

**cOID:** String.  
 Customer Order ID.  
 An arbitrary string that can be used to identify the order  
 The value must be unique for a 24h span.  
 Do not set this value for child orders when placing a bracket order.

**parentId:** String.  
 Only specify for child orders when placing bracket orders.  
 The parentId for the child order(s) must be equal to the cOId (customer order id) of the parent.

**orderType:** String. Required  
 The order-type determines what type of order you want to send.  
 Available Order Types: LMT, MKT, STP, STOP\_LIMIT, MIDPRICE, TRAIL, TRAILLMT

**listingExchange:** String.  
 Primary routing exchange for the order.  
 By default we use “SMART” routing.  
 Possible values are available via the endpoint: /iserver/contract/{conid}/info

**isSingleGroup:** bool.  
 Set to true if you want to place a single group orders(OCA)

**outsideRTH:** bool.  
 Set to true if the order can be executed outside regular trading hours.

**price:** float. Required for LMT or STOP\_LIMIT  
 This is typically the limit price.  
 For STP|TRAIL this is the stop price.  
 For MIDPRICE this is the option price cap.

**auxPrice:** float. Required for STOP\_LIMIT and TRAILLMT orders.  
 Stop price for STOP\_LIMIT and TRAILLMT orders.  
 You must specify both price and auxPrice for STOP\_LIMIT|TRAILLMT orders.

**side:** String. Required  
 Valid Values: SELL or BUY

**ticker:** String.  
 This is the underlying symbol for the contract.

**tif:** String. Required  
 The Time-In-Force determines how long the order remains active on the market.  
 Valid Values: GTC, OPG, DAY, IOC, PAX (CRYPTO ONLY).

**trailingAmt:** float. Required for TRAIL and TRAILLMT order  
 optional if order is TRAIL, or TRAILLMT.  
 When trailingType is amt, this is the trailing amount  
 When trailingType is %, it means percentage.

**trailingType:** String. Required for TRAIL and TRAILLMT order  
 This is the trailing type for trailing amount.  
 You must specify both trailingType and trailingAmt for TRAIL and TRAILLMT order  
 Valid Values: “amt” or “%”

**allOrNone:** Boolean. Determine if the order should be executed in it entirety at once (True), or if the order may be filled through multiple executions (False)

**customerAccount:** String. Required for Nondisclosed Omnibus Accounts  
 A unique identifier for each account within the Omnibus structure to signify the account holder being traded.  
 Best practice (Not Required): clients should look to hash this value, using something along the lines of 5 digits of SHA1 of the account number.  
 This should not be implemented for non-omnibus accounts.

**isProCustomer:** Boolean. Required for Nondisclosed Omnibus Accounts  
 Signify whether or not the subaccount is classified as Professional or Non-Professional.  
 This should not be implemented for non-omnibus accounts.

**referrer:** String.  
 Custom order reference

**quantity:** float. Required\*  
 Used to designate the total number of shares traded for the order.  
 Only whole share values are supported.

**cashQty:** float.  
 Used to specify the monetary value of an order instead of the number of shares.  
 When using ‘cashQty’ don’t specify ‘quantity’  
 Cash quantity orders are provided on a non-guaranteed basis.  
 Cash Quantity orders are only supported for Cryptocurrency and Forex contracts.

**fxQty:** float.  
 This is the cash quantity field which can only be used for Currency Conversion Orders.  
 When using ‘fxQty’ don’t specify ‘quantity’.

**useAdaptive:** boolean  
 If true, the system will use the Price Management Algo to submit the order.  
 Read more on our Price Management Algo page. https://www.interactivebrokers.com/en/index.php?f=43423

**isCcyConv:** boolean  
 set to true if the order is a FX conversion order

**allocationMethod:** String.  
 Set the allocation method when placing an order using an FA account for a group.  
 Based on value set in Trader Workstation.

**manualOrderTime:** int.  
 Only used for Brokers and Advisors. Mark the time to manually record initial order entry.  
 Must be sent as epoch time integer.

**deactivated:** bool.  
 Functions the same as [Saving an Order in Trader Workstation](/campus/trading-lessons/getting-started-with-the-order-entry-panel/).

**strategy:** String.  
 Specify which IB Algo algorithm to use for this order.

**strategyParameters:** Array.  
 The IB Algo parameters for the specified algorithm.  
 }]

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/U1234567/orders"
json_content = {
  "orders": [
    {
      "acctId": "U1234567",
      "conid": 265598,
      "conidex": "265598@SMART",
      "manualIndicator": True,
      "extOperator":"person1234",
      "secType": "265598@STK",
      "cOID": "AAPL-BUY-100",
      "parentId": None,
      "orderType": "TRAILLMT",
      "listingExchange": "NASDAQ",
      "isSingleGroup": false,
      "outsideRTH": true,
      "price": 185.50,
      "auxPrice": 183,
      "side": "BUY",
      "ticker": "AAPL",
      "tif": "GTC",
      "trailingAmt": 1.00,
      "trailingType": "amt",
      "referrer": "QuickTrade",
      "quantity": 100,
      # Can not be used in tandem with quantity value.
      # "cashQty": {{ cashQty }},
      # "fxQty": {{ fxQty }},
      "useAdaptive": false,
      "isCcyConv": false,
      # May specify an allocation method such as Equal or NetLiq for Financial Advisors.
      # "allocationMethod": {{ allocationMethod }},
      "strategy": "Vwap",
        "strategyParameters": {
          "MaxPctVol":"0.1",
          "StartTime":"14:00:00 EST",
          "EndTime":"15:00:00 EST",
          "AllowPastEndTime":true
        }
    }
  ]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account/U1234567/orders \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "orders": [
    {
      "acctId": "U1234567",
      "conid": 265598,
      "conidex": "265598@SMART",
      "manualIndicator": true,
      "extOperator":"person1234",
      "secType": "265598:STK",
      "cOID": "AAPL-BUY-100",
      "parentId": null,
      "orderType": "TRAILLMT",
      "listingExchange": "ISLAND",
      "isSingleGroup": false,
      "outsideRth": true,
      "price": 185.50,
      "auxPrice": 183,
      "side": "BUY",
      "ticker": "AAPL",
      "tif": "GTC",
      "trailingAmt": 1.00,
      "trailingType": "amt",
      "referrer": "QuickTrade",
      "quantity": 100,
      # Can not be used in tandem with quantity value.
      # "cashQty": {{ cashQty }}, 
      # "fxQty": {{ fxQty }},
      "useAdaptive": false,
      "isCcyConv": false,
      # May specify an allocation method such as Equal or NetLiq for Financial Advisors.
      # "allocationMethod": {{ allocationMethod }},
      "strategy": "Vwap",
        "strategyParameters": {
          "MaxPctVol":"0.1",
          "StartTime":"14:00:00 EST",
          "EndTime":"15:00:00 EST",
          "AllowPastEndTime":true
        }
    }
  ]
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

Users that wish to avoid receiving /reply message should consider using the [Suppression](/campus/ibkr-api-page/cpapi-v1/#questions-suppress) endpoint to automatically accept them.

**Important:** The reply must be confirmed before sending any further orders. Otherwise, the order will be invalidated and attempts to confirm invalid replies will result in a timeout (503).

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
    "id": "07a13a5a-4a48-44a5-bb25-5ab37b79186c",
    "message": [
      "The following order \"BUY 5 AAPL NASDAQ.NMS @ 150.0\" price exceeds \nthe Percentage constraint of 3%.\nAre you sure you want to submit this order?"
    ],
    "isSuppressed": false,
    "messageIds": [
      "o163"
    ]
  }
]
```

#### Order Reject Object

In the event an order is placed that can not be completed based on account details such as trading permissions or funds, customers will receive a 200 OK response along with an error message explaining the issue.

This is unique from the 200 response used in the Alternate Response Object, or a potential 500 error resulting from invalid request content.

```
{
  "error":"We cannot accept an order at the limit price you selected. Please submit your order using a limit price that is closer to the current market price of 197.79.  Alternatively, you can convert your order to an Algorithmic Order (IBALGO)."
}
```
