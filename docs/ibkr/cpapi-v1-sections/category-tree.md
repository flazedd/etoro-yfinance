### Event contract category and market tree Copy Location

Provides event contract category and market tree

`GET /v1/api/forecast/category/tree`

#### Request Object

No params or body content should be sent.

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

**categories:** list  
 List of categories

**id:** string  
 Category identifier

**name:** string  
 Category name

**parent\_id:** string  
 Identifier of parent category, optional

**markets:** list  
 List of markets, optional

**name:** string  
 Market name

**symbol:** string  
 Market symbol

**exchange:** string  
 Market exchange

**conid:** integer  
 Market contract identifier

**as\_of:** string  
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
```
