### Historical Market Data Request Copy Location

For streaming historical data, the topic smh+Id is used. There are also optional parameters available in JSON format. If no parameters are specified, the empty parameters array {} can be passed. Incorrectly specified parameters are ignored and the default (empty) response is returned.

**NOTE:** Only a max of 5 concurrent historical data request available at a time.

**NOTE:** Historical data will only respond once, though customers will still need to unsubscribe from the endpoint.

#### Historical Data Request

###### Topic:

**smh**  
 Subscribes the user to historical bar data.  
 Streaming, top-of-the-book, level one, historical data is available for all instruments using Client Portal API’s websocket endpoint.

###### Topic Target:

**conids:** Required.  
 Must pass a single contract identifier.  
 Contracts requested use SMART routing by default. To specify the exchange, the contract identifier should be modified to: conId@EXCHANGE, where EXCHANGE is the requested data source.

###### Arguments:

**exchange:** String.  
 Requested exchange to receive data.

**period:** String.  
 Total duration for which bars will be requested.

**bar:** String.  
 Interval of time to receive data.

**outsideRth:** Bool.  
 Determines if you want data outside regular trading hours (true) or only during market hours (false).

**source:** String.  
 The value determining what type of data to show.

**format:** String.  
 The format in which bars are returned.

```
smh+conid+{
    "exchange":"exchange",
    "period":"period",
    "bar":"bar",
    "outsideRth":outsideRth,
    "source":"source",
    "format":"format"
}
```

#### Historical Data Response

**serverId:** String.  
 Request identifier for the specific historical data request. Used for cancelling the data stream.

**symbol:** String.  
 Returns the symbol for the requested conid.

**text:** String.  
 Company long name.

**priceFactor:** int.  
 Price mutlipler (based on $0.01)

**startTime:** String.  
 Returns the starting time (in epoch time) of the response.

**high:** String.  
 Returns the highest “high value/Volume value/Outside RTH volume” of the period.

**low:** String.  
 Returns the lowest “Low value/Volume value/Outside RTH volume” of the period.

**timePeriod:** String.  
 Returns the period covered by the request.

**barLength:** int.  
 Returns the string length of the bar response.

**mdAvailability:** String.  
 Internal IBKR message.

**mktDataDelay:** int.  
 Returns if there is any delay in the market data.

**outsideRth:** Bool.  
 Returns if the data contains information outside regular trading hours.

**volumeFactor:** int.  
 Determines if the volume is returned as lots, multipliers, or as-is.

**priceDisplayRule:** int.  
 Internal IBKR message.

**priceDisplayValue:** String.  
 Internal IBKR message.

**negativeCapable:** Bool.  
 Returns contract rule whether the contract supports negative values or not.

**messageVersion:** int.  
 Internal IBKR message.

**data:** Array of Objects.  
 Returns all bars related that fall within the period.

**o**: float.  
 Opening value for the bar’s duration.

**c**: float.  
 Closing value for the bar’s duration.

**l**: float.  
 Lowest value for the bar’s duration.

**h**: float.  
 Highest value for the bar’s duration.

**v:** int.  
 Total volume of the bar.

**t:** int.  
 Epoch time of the bar return.

**points:** int.  
 Displays the total number of bars returned within ‘data’.

**topic:** String.  
 Represents the request sent.

```
{
    "serverId": "serverId",
    "symbol": "symbol",
    "text": "text",
    "priceFactor": priceFactor,
    "startTime": "startTime",
    "high": "high",
    "low": "low",
    "timePeriod": "timePeriod",
    "barLength": barLength,
    "mdAvailability": "mdAvailability",
    "mktDataDelay": mktDataDelay,
    "outsideRth": outsideRth,
    "volumeFactor": volumeFactor,
    "priceDisplayRule": priceDisplayRule,
    "priceDisplayValue": "priceDisplayValue",
    "negativeCapable": negativeCapable,
    "messageVersion": messageVersion,
    "data": [data],
    "points": points, 
    "topic": "topic",
}
```

The historical market data request takes the following parameters:

| Parameter | Description | Valid Values |
| --- | --- | --- |
| exchange: String | Contract exchange | Valid exchange on which the contract trades |
| period: String | Request duration | - {1-30}min - {1-8}h - {1-1000}d - {1-792}w - {1-182}m - {1-15}y |
| bar: String | Request bar size | - 1min - 2min - 3min - 5min - 10min - 15min - 30min - 1h - 2h - 3h - 4h - 8h - 1d - 1w - 1m |
| outsideRTH: Boolean | Request data outside trading hours | true/false |
| source: String | Type of date requested | - midpoint - trades - bid\_ask - bid - ask |
| format: String | Historical values returned | - %o – open - %c – close - %h – high - %l – low - %v – volume |
