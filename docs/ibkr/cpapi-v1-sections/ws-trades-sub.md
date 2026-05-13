### Request Trades data Copy Location

#### Trades Data Request

###### Topic:

**str**  
 Subscribes the user to trades data. This will return all executions data while streamed.

###### Arguments:

**realtimeUpdatesOnly:** bool. Optional  
 Decide whether you want to display any historical executions, or only the executions available in real time.  
 Set to false by default.

**days:** int. Optional  
 Returns the number of days of executions for data to be returned.  
 Set to 1 by default.

```
str+{
    "realtimeUpdatesOnly":realtimeUpdatesOnly, 
    "days":days
}
```

#### Trades Data Response

**topic:** String.  
 Returns the topic of the given request.

**args:** Object.  
 Returns the object containing the pnl data.

**execution\_id:** String.  
 Execution identifier of the specific trade.

**symbol:** String.  
 Ticker symbol of the traded contract.

**supports\_tax\_opt:** String.  
 Determines if the contract supports the tax optimizer. Client Portal only.

**side:** String.  
 Determines if the order was a buy or sell side.

**order\_description:** String.  
 Describes the full content of the order.  
 Value format: “{SIDE} {SIZE} @ {PRICE} on {EXCHANGE}”

**trade\_time:** String.  
 Traded date time in UTC.  
 Value format: “YYYYMMDD-HH:mm:ss”

**trade\_time\_r:** int.  
 Traded datetime of the execution in epoch time.

**size:** float.  
 Returns the quantity of shares traded.

**order\_ref:** string.  
 Returns the custom order identifier (cOID) from order placement.

**price:** String.  
 Returns the price used for the given trade.

**exchange:** String.  
 Returns the exchange the order executed at.

**net\_amount:** float.  
 Returns the total amount traded after calculating multiplier.

**account:** String.  
 Returns the account the order was traded on.

**accountCode:** String.  
 Returns the account the order was traded on.

**company\_name:** String.  
 Returns the title of the company for the contract.

**contract\_description\_1:** String.  
 Returns the underlying symbol of the contract.

**contract\_description\_2:** String.  
 Returns a full description of the derivative.

**sec\_type:** String.  
 Returns the security type traded.

**conid:** int.  
 Contract identifier for the traded contract.

**conidEx:** String.  
 Returns the conidEx of the order if specified. Otherwise returns conid.

**open\_close:** String.  
 Returns if the execution was a closing trade.  
 Returns “???” if the position was already open, but not a closing order.

**liquidation\_trade:** String.  
 Returns if the trade was a result of liquidation.

**is\_event\_trading:** String.  
 Determines if the order can be used with EventTrader.

```
{
  "topic":"topic"
  "args":[
    {
    "execution_id":"execution_id"
    "symbol":"symbol"
    "supports_tax_opt":"supports_tax_opt"
    "side":"side"
    "order_description":"order_description"
    "trade_time":"trade_time"
    "trade_time_r":trade_time_r
    "size":size
    "order_ref": "order_ref"
    "price":"price"
    "exchange":"exchange"
    "net_amount":net_amount
    "account":"account"
    "accountCode":"accountCode"
    "company_name":"company_name"
    "contract_description_1":"contract_description_1"
    "contract_description_2":"contract_description_2"
    "sec_type":"sec_type"
    "conid":conid
    "conidEx":"conidEx"
    "open_close":"open_close"
    "liquidation_trade":"liquidation_trade"
    "is_event_trading":"is_event_trading"
    }
  ]
}
```
