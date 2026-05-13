### Market Data Request Copy Location

#### Market Data Request

###### Topic:

**smd**  
 Subscribes the user to watchlist market data.  
 Streaming, top-of-the-book, level one, market data is available for all instruments using Client Portal API’s websocket endpoint.

**IMPORTANT:** Market data streams will terminate after 15 minutes. Users must send a new request for market data after 10 minutes to continue retrieving data for the instrument.  
 **NOTE:** The maximum number of market data subscriptions is based on your account’s [Market Data Lines](/campus/ibkr-api-page/market-data-subscriptions/#market-data-lines).

###### Topic Target:

**conid:** Required.  
 Must pass a single contract identifier.  
 Contracts requested use SMART routing by default. To specify the exchange, the contract identifier should be modified to: conId@EXCHANGE, where EXCHANGE is the requested data source.  
 Combos or Spreads market data can be retrieved using identical formatting to [Combo or Spread Orders](/campus/ibkr-api-page/cpapi-v1/#combo-orders). The only difference is that a spread\_conid of 0 must be passed.

###### Arguments:

**fields:** Array of Strings. Optional.  
 Pass an array of field IDs. Each ID should be passed as a string.  
 You can find a list of fields in the Market Data Fields section.

```
smd+conId+{
    [
    "fields":"field_1",
    "field_2",
    "field_n", 
    "field_n+1"
    ]
}
```

Watchlist market data at Interactive Brokers is derived from time-based snapshot intervals which vary by product and region. This means that a given tick will only update as frequently as its interval allows. See the table for more details on product specifics.

| Product | Frequency |
| --- | --- |
| All Products | 500ms |

#### Market Data Response

**server\_id:** String.  
 Returns the request’s identifier.

**conidEx:** String.  
 Returns the passed conid field. May include exchange if specified in request.

**conid:** int.  
 Returns the contract id of the request

**\_updated:** int\*.  
 Returns the epoch time of the update in a 13 character integer .

**6119:** String.  
 Field value of the server\_id. Returns the request’s identifier.

**fields\*:** String.  
 Returns a response for each request. Some fields not be as readily available as others. See the [Market Data](/campus/ibkr-api-page/cpapi-v1/#market-data) section for more details.

**6509:** String.  
 Returns a multi-character value representing the Market Data Availability.

**topic:** String.  
 Restates the requesting topic.

```
{
    "server_id":"server_id",
    "conidEx":"conidEx",
    "conid":conid,"
    _updated":_updated,
    "6119":"serverId",
    "field_1":field_1,
    "field_2":field_2,
    "field_n":field_n, 
    "field_n+1":field_n+1,
    "6509":"RB",
    "topic":"smd+conid"
}
```
