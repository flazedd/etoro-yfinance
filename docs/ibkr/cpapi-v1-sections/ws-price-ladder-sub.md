### Subscribe to BookTrader Price Ladder Copy Location

#### Price Ladder Request

###### Topic:

**sbd**  
 Subscribes the user to BookTrader price ladder data.  
 Streaming BookTrader data requires users to maintain a L2, Depth of Book, market data subscription. See the [Market Data Subscriptions page](/campus/ibkr-api-page/market-data-subscriptions/#popular-md-subscriptions) for more details.

###### Topic Target:

**acctId:** Required.  
 Must pass a single AccountId.

**conids:** Required.  
 Must pass a single contract identifier.

**exchange:** Optional.  
 Provide a routing exchange identifier.  
 If no exchange is specified, all available deep exchanges are assumed.

```
sbd+acctId+conid+exchange
```

#### Price Ladder Response

**topic:** String.  
 Returns the request’s topic string.

**data:** Array of Objects.  
 Returns an array of objects to indicate ladder depth.

**row:** int.  
 Returns the row identifier of the ladder data.

**focus:** int.  
 Indicates if the value was marked as the last trade price for the contract.

**price:** String.  
 Returns the Last, or last executed trade, price.  
 In some instances, price and size will be returned in the structure ‘”price”:”size @ price”‘.

**ask:** String.  
 Returns the corresponding ask size.

**bid:** String.  
 Returns the corresponding bid size.

```
{
  "topic":"sbd+acctId+conid",
  "data":[
    {"row":0,"focus":0,"price":"price"},
    {"row":1,"focus":0,"price":"size @ price"},
    {"row":n,"focus":0,"price":"price", "bid":"bid"},
    {"row":n+1,"focus":0,"price":"price", "ask":"ask"},
    {"row":n+1,"focus":0,"price":"size @ price", "ask":"ask"}
  ]
}
```
