### Request Live Order Updates Copy Location

As long as an order is active, it is possible to retrieve it using Client Portal API. Live streaming orders can be requested by subscribing to the sor topic. Once live orders are requested we will start to relay back when there is an update. To receive all orders for the current day the endpoint /iserver/account/orders can be used. It is advised to query all orders for the current day first before subscribing to live orders.

#### Order Updates Request

###### Topic:

**sor**  
 Subscribes the user to live order updates.

###### Arguments:

**filters**: Array of String  
 Pass an array with a single string indicating exclusive [Order Status Value](/campus/ibkr-api-page/cpapi-v1/#order-status-value) to return.

```
sor+{"filters":["Submitted"]}
```

#### Order Updates Response

**topic:** String.

**args:** Array of Objects.

**acct:** String.  
 Returns the account Id of which account made the request.

**conid:** int.  
 Contract Identifier for the given order.

**orderId:** int.  
 Order identfier affiliated with the given order.

**cashCcy:** String.  
 Base currency used for the transaction.

**sizeAndFills:** String.  
 Total quantity filled in the order.

**orderDesc:** String.  
 Order description of the given order.  
 Describes the side, size, orderType, price, and tif of the orer.

**description1:** String.  
 Ticker symbol of the request.

**ticker:** String.  
 Ticker symbol of the request.

**secType:** String.  
 Security type of the request.

**listingExchange:** String.  
 Primary exchange where the contract is held.

**remainingQuantity:** float.  
 Percentage of the order quantity remaining.

**filledQuantity:** float.  
 Percentage of the ordr quantity filled.

**companyName:** String.  
 Longname of the contract’s company.

**status:** String.  
 Current order status.  
 Value Format: Presubmitted, Submitted, Filled, Cancelled.

**origOrderType:** String.  
 Returns the original order type of the given order.

**supportsTaxOpt:** String.  
 Determines if the order supports Tax Optimizer.

**lastExecutionTime:** String.  
 Returns the datetime object of the most recent execution.

**lastExecutionTime\_r:** int.  
 Returns the epoch timestamp of the most recent execution.

**order\_ref:** string.  
 Returns the custom order identifier (cOID) from order placement.

**orderType:** String.  
 Returns the current order type of the order.  
 Value Format: MARKET, LIMIT, STOP

**side:** String.  
 Returns the side of the trade.  
 Value Format: BUY, SELL

**timeInForce:** String.  
 Returns the time in force for the given order.

**price:** int.  
 Provides the limit or stop price for the submitted order.

**bgColor:** String.  
 Background color. Used for Client Portal only.

**fgColor:** String.  
 Foreground color. Used for Client Portal only.

```
{
    "topic": "sor" ,
    "args": [
        {
            "acct": "acct",
            "conid": conid,
            "orderId": orderId,
            "cashCcy": "cashCcy",
            "sizeAndFills": "sizeAndFills",
            "orderDesc": "orderDesc",
            "description1": "description1",
            "ticker": "ticker",
            "secType": "secType",
            "listingExchange": "listingExchange",
            "remainingQuantity": remainingQuantity,
            "filledQuantity": filledQuantity,
            "companyName": "companyName",
            "status": "status",
            "origOrderType": "origOrderType",
            "supportsTaxOpt": "supportsTaxOpt",
            "lastExecutionTime": "lastExecutionTime",
            "lastExecutionTime_r": lastExecutionTime_r,
            "order_ref": "order_ref,
            "orderType": "orderType",
            "side": "side",
            "timeInForce": "timeInForce",
            "price": price,
            "bgColor": "#000000",
            "fgColor": "#00F000"
        }
    ]
}
```
