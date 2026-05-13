### Contract details Copy Location

Provides contract rules for specific event binary options

`GET /forecast/contract/details`

#### Request Object

###### Query Params

**conid:** Integer  
 Contract identifier

- Python
- cURL

```
import requests

url = "{{base-url}}/forecast/contract/details?conid=767285167"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

```
curl --location --globoff '{{base-url}}/forecast/contract/details?conid=767285167'
```

#### Response Object

**conid\_yes:** Integer  
 Contract id of “yes” contract

**conid\_no:** Integer  
 Contract id of “no” contract

**question:** String  
 Contract question(i.e “Will this happen on this date?”)

**side:** String  
 “Y” or “N” – yes or no contract

**strike\_label:** String  
 Strike label to display

**strike:** Double  
 Contract strike

**exchange:** String  
 Contract exchange

**expiration:** String  
 Contract expiration

**symbol:** String  
 Contract symbol

**logo\_category:** String

**measured\_period:**

**market\_name:** String  
 Name of contract’s market

**unerlying\_conid:** Integer  
 Underlying asset of the contract

```
{
    "conid_yes": 767285167,
    "conid_no": 767285169,
    "question": "Will Stacey Abrams win the Georgia Democratic primary for governor in 2026?",
    "side": "Y",
    "strike_label": "Stacey Abrams",
    "strike": 1.0,
    "exchange": "FORECASTX",
    "expiration": "20260612",
    "symbol": "GPGAD",
    "category": "g7428",
    "logo_category": "g17467",
    "measured_period": "May19'26",
    "market_name": "Georgia Governor Democratic Primary",
    "underlying_conid": 766914406,
    "payout": 1.0
}
```
