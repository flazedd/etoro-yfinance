### Contract Rules Copy Location

Provides contract rules for specific binary options.

`GET /forecast/contract/rules`

#### Request Object

###### Query Params

**conid:** Integer  
 Contract identifier

- Python
- cURL

```
import requests

url = "{{base-url}}/forecast/contract/rules?conid=767285167"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

```
curl --location --globoff '{{base-url}}/forecast/contract/rules?conid=767285167'
```

#### Response Object

**asset\_class:** String  
 Product asset class

**description:** String  
 Product description

**market\_name:** String  
 Name of contract’s market

**measured\_period:** String

**threshold:** String  
 Either strike or strike label depending on the contract

**source\_agency:** String  
 Name of source agency

**data\_and\_resolution\_link:** String  
 Link to data from source agency

**last\_trade\_time:**  Long  
 Last trade time in EPOCH

**product\_code:** String  
 Product code, symbo

**market\_rules\_link:** String  
 Link to market rules document

**release\_time:** Long  
 Release time in EPOCH seconds

**payout\_time:** Long  
 Payout time in EPOCH seconds

**payout:** String  
 Formatted payout amount

**price\_increment:** String  
 Formatted price increment amount

**exchange\_timezone:** String  
 Exchange timezone

```
{
    "asset_class": "OPT",
    "description": "The Georgia Democratic Gubernatorial Primary determines the party nominee for governor, shaping state leadership and national political influence.",
    "market_name": "Georgia Governor Democratic Primary",
    "measured_period": "May19'26",
    "threshold": "Stacey Abrams",
    "source_agency": "Georgia Secretary of State Elections Division",
    "data_and_resolution_link": "https://sos.ga.gov/index.php/elections",
    "last_trade_time": 1781301540,
    "product_code": "GPGAD",
    "market_rules_link": "https://data.forecastex.com/regulatory/GPTermsandConditions.pdf",
    "release_time": 1781301540,
    "payout_time": 1781373600,
    "payout": "$1.00",
    "price_increment": "$0.01",
    "exchange_timezone": "US/Central"
}
```
