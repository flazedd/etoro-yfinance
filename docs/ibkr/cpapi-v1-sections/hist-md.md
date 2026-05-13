### Historical Market Data Copy Location

Get historical market Data for given conid, length of data is controlled by ‘period’ and ‘bar’.

**Note**:

- There’s a limit of 5 concurrent requests. Excessive requests will return a ‘Too many requests’ status 429 response.
- This endpoint provides a maximum of 1000 data points.

```
GET /iserver/marketdata/history
```

#### Request Object

###### Query Params

**conid:** String. Required  
 Contract identifier for the ticker symbol of interest.

**exchange:** String.  
 Returns the exchange you want to receive data from.

**period:** String.  
 Overall duration for which data should be returned.  
 Default to 1w  
 Available time period– {1-30}min, {1-8}h, {1-1000}d, {1-792}w, {1-182}m, {1-15}y

**bar:** String. Required  
 Individual bars of data to be returned.  
 Possible value– 1min, 2min, 3min, 5min, 10min, 15min, 30min, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1m.  
 Formatted as: min=minute, h=hour, d=day, w=week, m=month, y=year  
 See *Step Size* below to ensure your Bar Size is supported for your chosen Period value.

**startTime:** String  
 Starting date of the request duration.

**outsideRth:** bool.  
 Determine if you want data after regular trading hours.

**source:** String.  
 Type of data to be returned.  
 Possible value– Trades, Midpoint, Bid\_Ask  
 Trades is passed by default.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/marketdata/history?conid=265598&exchange=SMART&period=1d&bar=1d&startTime=20230821-13:30:00&outsideRth=true&source=Midpoint"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/marketdata/history?conid=265598&exchange=SMART&period=1d&bar=1h&startTime=20230821-13:30:00&outsideRth=true \ 
--request GET
```

#### Step Size

A step size is the permitted minimum and maximum bar size for any given period.

|  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| period | 1min | 1h | 1d | 1w | 1m | 3m | 6m | 1y | 2y | 3y | 15y |
| bar | 1min | 1min – 8h | 1min – 8h | 10min – 1w | 1h – 1m | 2h – 1m | 4h – 1m | 8h – 1m | 1d – 1m | 1d – 1m | 1w – 1m |
| default bar | 1min | 1min | 1min | 15min | 30min | 1d | 1d | 1d | 1d | 1w | 1w |

#### Response Object

**serverId:** String.  
 Internal request identifier.

**symbol:** String.  
 Returns the ticker symbol of the contract.

**text:** String.  
 Returns the long name of the ticker symbol.

**priceFactor:** String.  
 Returns the price increment obtained from the display rules.

**startTime:** String.  
 Returns the initial time of the historical data request.  
 Returned in UTC formatted as YYYYMMDD-HH:mm:ss

**high:** String.  
 Returns the High values during this time series with format %h/%v/%t.  
 %h is the high price (scaled by priceFactor),  
 %v is volume (volume factor will always be 100 (reported volume = actual volume/100))  
 %t is minutes from start time of the chart

**low:** String.  
 Returns the low value during this time series with format %l/%v/%t.  
 %l is the low price (scaled by priceFactor),  
 %v is volume (volume factor will always be 100 (reported volume = actual volume/100))  
 %t is minutes from start time of the chart

**timePeriod:** String.  
 Returns the duration for the historical data request

**barLength:** int.  
 Returns the number of seconds in a bar.

**mdAvailability:** String.  
 Returns the Market Data Availability.  
 See the Market Data Availability section for more details.

**mktDataDelay:** int.  
 Returns the amount of delay, in milliseconds, to process the historical data request.

**outsideRth:** bool.  
 Defines if the market data returned was inside regular trading hours or not.

**volumeFactor:** int.  
 Returns the factor the volume is multiplied by.

**priceDisplayRule:** int.  
 Presents the price display rule used.  
 For internal use only.

**priceDisplayValue:** String.  
 Presents the price display rule used.  
 For internal use only.

**negativeCapable:** bool.  
 Returns whether or not the data can return negative values.

**messageVersion:** int.  
 Internal use only.

**data:** Array of objects.  
 Returns all historical bars for the requested period.  
 [{  
 **o:** float.  
 Returns the Open value of the bar.

**c:** float.  
 Returns the Close value of the bar.

**h:** float.  
 Returns the High value of the bar.

**l:** float.  
 Returns the Low value of the bar.

**v:** float.  
 Returns the Volume of the bar.

**t**: int.  
 Returns the Operator Timezone Epoch Unix Timestamp of the bar.  
 }],

**points:** int.  
 Returns the total number of data points in the bar.

**travelTime:** int.  
 Returns the amount of time to return the details.

```
{
  "serverId": "20477",
  "symbol": "AAPL",
  "text": "APPLE INC",
  "priceFactor": 100,
  "startTime": "20230818-08:00:00",
  "high": "17510/472117.45/0",
  "low": "17170/472117.45/0",
  "timePeriod": "1d",
  "barLength": 86400,
  "mdAvailability": "S",
  "mktDataDelay": 0,
  "outsideRth": true,
  "tradingDayDuration": 1440,
  "volumeFactor": 1,
  "priceDisplayRule": 1,
  "priceDisplayValue": "2",
  "chartPanStartTime": "20230821-13:30:00",
  "direction": -1,
  "negativeCapable": false,
  "messageVersion": 2,
  "data": [
    {
      "o": 173.4,
      "c": 174.7,
      "h": 175.1,
      "l": 171.7,
      "v": 472117.45,
      "t": 16923456000
    }
  ],
  "points": 0,
  "travelTime": 48
}
```

#### 500 System Error

**error:**  String.

```
{
  'error': 'description'
}
```

#### 429 Too many requests

**error:**  String.

```
{
  'error': 'description'
}
```
