### Trading Schedule (NEW) Copy Location

Returns the trading schedule for the 6 total days surrounding the current trading day. Non-Trading days, such as holidays, will not be returned.

`GET /contract/trading-schedule`

#### Request Object

###### Query Params

**conid:** *String.* Required  
 Provide the contract identifier to retrieve the trading schedule for.

**exchange:** *String.*  
 Accepts the exchange to retrieve data from. Primary exchange is assumed by default.

- Python
- cURL

```
request_url = f"{baseUrl}/contract/trading-schedule?conid=265598&exchange=ISLAND"
requests.get(url=requests_url)
```

```
curl \
--url {{baseUrl}}/contract/trading-schedule?conid=265598&exchange=ISLAND \
--request GET
```

#### Response Object

**exchange\_time\_zone:** String.  
 Returns the time zone the exchange trades in.

**schedules:** Object.  
 A schedule object containing the trading hours.  
 {  
 **{date}:** Array.  
 Array of hours objects detailing extended and standard trading.  
 [  
 **extended\_hours:** Array.  
 Reference the total extended trading hours for the session.  
 {  
 **cancel\_daily\_orders:** Boolean.  
 Determines if DAY orders are canceled after ‘closing’ time.

**closing:** Integer.  
 Epoch timestamp of the exchange’s close.

**opening:** Integer.  
 Epoch timestamp of the exchange’s open.  
 }

**liquid\_hours:** Array.  
 Reference the available trading hours for the regular session  
 {  
 **closing:** Integer.  
 Epoch timestamp of the exchange’s close.

**opening:** Integer.  
 Epoch timestamp of the exchange’s open.  
 }]}

```
{
  'exchange_time_zone': 'US/Central', 
  'schedules': {
    '20251218': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766095200,
        'opening': 1766012400}],
    'liquid_hours': [{
        'closing': 1766095200,
        'opening': 1766068200
    }]},
    '20251219': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766181600,
        'opening': 1766098800}],
    'liquid_hours': [{
        'closing': 1766181600,
        'opening': 1766154600
    }]},
    '20251222': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766440800,
        'opening': 1766358000}],
    'liquid_hours': [{
        'closing': 1766440800,
        'opening': 1766413800
    }]},
    '20251223': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766527200,
        'opening': 1766444400
		}],
    'liquid_hours': [{
        'closing': 1766527200,
        'opening': 1766500200
    }]},
    '20251224': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766600100,
        'opening': 1766530800}],
    'liquid_hours': [{
        'closing': 1766600100,
        'opening': 1766586600
    }]},
    '20251226': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766786400,
        'opening': 1766703600
    }]}	
  }
}
```
