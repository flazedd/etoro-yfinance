### Categorization Copy Location

ForecastEx forecast contracts are sorted into a category hierarchy for organizational purposes.

These categories are metadata rather than immutable attributes of the tradable instruments themselves – they can be expected to change slightly over time.

This category tree is three levels deep, and its leaves (the level 3 categories) contain the forecast contracts “Markets” — groups of tradable contracts sharing questions of the same form e.g. “will the Fed Funds rate on X date exceed Y percent”.

The `/forecast/category/tree` endpoint can be used to retrieve the complete category tree.

Returns event contract category and market tree

`GET /forecast/category/tree`

#### Request Object

###### No Body Params

- Python
- cURL

```
import requests

url = "{{base-url}}/forecast/category/tree"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
```

```
curl --location --globoff '{{base-url}}/forecast/category/tree'
```

#### Response Object

**categories:** List  
 List of categories

**id:** String  
 Category identifier

**name:** String  
 Category name

**parent\_id:** String  
 Identifier or parent category, optional

**markets:** List  
 List of markets, optional

**name:** String  
 Market name

**symbol:** String  
 Market symbol

**exchange:** String  
 Market exchange

**conid:** Integer  
 Market contract identifier

**as\_of:** String  
 Timestamp of data retrieval

```
{
    "categories": {
        "g78664": {
            "name": "Northeast",
            "parent_id": "g17457",
            "markets": [
                {
                    "name": "Northeastern US CPI",
                    "symbol": "RCNET",
                    "exchange": "FORECASTX",
                    "conid": 831072285,
                    "product_conid": 831072289
                }
            ]
        },
}
```
