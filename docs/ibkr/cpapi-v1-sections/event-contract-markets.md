### Markets and Strikes Copy Location

ForecastEx forecast contracts are modeled as options or futures options, depending on the event they resolve against.

Because they are derivative products, they are always listed against an underlier. Presently forecast contract underliers are either an index or futures contract. The underliers will have their own contract IDs separate from the contract IDs of the forecast contracts.

These underlier contract IDs can be used to retrieve relevant historical data sets for the underlying event, where available. For example, the GT (Global Temperature) contracts are listed against a GT index, and the index data set is historical global temperature data sourced from NOAA.

In all cases, a Market has a symbol, mirroring options. Examples: FF, HORC, USIP

Forecast contracts, like options, have a strike and expiration. Strike value need not be numeric; for instance, for election-related contracts it will be a candidate’s name. The strikeLabel field in the `/contracts` response delivers these strings.

All contracts have a true expiration which is the resolution time mentioned above after which the contract is considered resolved and it ceases to exist.

A fully specified question, including the strike value and measured period, is referred to as a “strike” – similar to a specific strike row in a two-sided option chain table.

Each such strike has two contracts associated with it: YES and NO.

IBKR assigns a separate contract ID to both the YES and NO contracts of a given strike.

Following from the options model: YES is a Call, and NO is a Put.

For each contract:

- The long (and canonical) form of this question is delivered in the longDescription field.
- A shortened options-style form is delivered in the shortDescription field.

Note that YES and NO contracts each have their own bid/ask/last data.

Provides all contracts for given underlyin market

`GET /forecast/contract/market`

#### Request Object

###### Query Params

**underlyingConid:** Integer  
 name of contract’s market

**exchange:** String

- Python
- cURL

```
import requests

url = "{{base-url}}/forecast/contract/market?underlyingConid=766914406&exchange=FORECASTX"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

```
curl --location --globoff '{{base-url}}/forecast/contract/market?underlyingConid=766914406&exchange=FORECASTX'
```

#### Response Object

**market\_name:** String  
 Name of contract’s market

**exchange:** String  
 Exchange that was passed in request

**symbol:** String  
 Market symbol

**logo\_category:** String

**exclude\_historical\_data:** Bool

**payout:**  Double

**contracts:** List

**conid:** Integer  
 Market contract identifier

**side:** String  
 Y or N, yes or no contract

**expiration:** String  
 Contract expiration date in YYYYMMDD format

**strike:** Double  
 Contract strike

**strike\_label:** String

**expiry\_label:** String

**underlying\_conid**Integer  
 Underlying asset of the contract

```
{
    "market_name": "Georgia Governor Democratic Primary",
    "exchange": "FORECASTX",
    "symbol": "GPGAD",
    "logo_category": "g17467",
    "exclude_historical_data": true,
    "payout": 1.0,
    "contracts": [
        {
            "conid": 767285167,
            "side": "Y",
            "expiration": "20260612",
            "strike": 1.0,
            "strike_label": "Stacey Abrams",
            "expiry_label": "2026",
            "underlying_conid": 766914406,
            "time_specifier": "2026.5.19"
        },
}
```
