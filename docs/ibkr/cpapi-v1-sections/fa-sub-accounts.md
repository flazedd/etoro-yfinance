### Allocatable Sub-Accounts Copy Location

Retrieves a list of all sub-accounts and returns their net liquidity and available equity for advisors to make decisions on what accounts should be allocated and how.

`GET /iserver/account/allocation/accounts`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/allocation/accounts" 
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/account/allocation/accounts \
--request GET
```

#### Response Object

**accounts:** Array of objects.  
 Array containing all sub-accounts held by the advisor.  
 [{  
 **data:** Array of objects.  
 Contains Net liquidation and available equity of the given account Id.  
 [{  
 **value:** String.  
 Contains the price value affiliated with the key.

**key:** String.  
 Defines the value of the object.  
 Expected values: “AvailableEquity”, “NetLiquidation”  
 }]  
 **name:** String.  
 Returns the account ID affiliated with the balance data.  
 }]

```
{
  "accounts": [
    {
      "data": [
        {
          "value": "2677.89",
          "key": "NetLiquidation"
        },
        {
          "value": "2134.76",
          "key": "AvailableEquity"
        }
      ],
      "name": "U123456"
    },
    {
      "data": [
        {
          "value": "1200.88",
          "key": "NetLiquidation"
        },
        {
          "value": "1000.56",
          "key": "AvailableEquity"
        }
      ],
      "name": "U456789"
    }
  ]
}
```
