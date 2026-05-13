### Portfolio Allocation (All) Copy Location

Similar to /portfolio/{accountId}/allocation but returns a consolidated view of of all the accounts returned by /portfolio/accounts. /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint.

`POST /portfolio/allocation`

#### Request Object

###### Body Params

**acctIds:** Array of Strings. Required  
 Contains all account IDs as strings the user should receive data for.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/allocation"
json_content = {
  "acctIds": [
    "U1234567",
    "U4567890"
  ]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/portfolio/allocation \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "acctIds": [
    "U1234567",
    "U4567890"
  ]
}'
```

**assetClass:** Object.  
 Contains details pertaining to specific security types.  
 {  
 **long:** Object.  
 Returns the value of the asset class currently traded long.

**short:** Object.  
 Returns the value of the asset class currently traded short.  
 },

**sector:** Object.  
 Contains details pertaining to specific trade sectors.  
 {  
 **long:** Object.  
 Returns the value of the trade sector currently traded long.

**short:** Object.  
 Returns the value of the trade sector currently traded short.  
 },

**group:** Object.  
 Contains details pertaining to specific industry groups.  
 {  
 **long:** Object.  
 Returns the value of the industry group currently traded long.

**short:** Object.  
 Returns the value of the industry group currently traded short.  
 }

```
{
  "assetClass": {
    "long": {
      "OPT": 27.12,
      "STK": 316441.2320366,
      "CASH": 2.1510102008312488E8
    },
    "short": {
      "OPT": -30.0,
      "CASH": -25.923946709036827
    }
  },
  "sector": {
    "long": {
      "Others": 5624.600040692091,
      "Technology": 237014.72999999998,
      "Industrial": 43077.12,
      "Consumer, Cyclical": 22453.78620745659,
      "Financial": 2503.3599999999997,
      "Communications": 5126.98,
      "Consumer, Non-cyclical": 667.7757884514332
    },
    "short": {
      "Others": -30.0
    }
  },
  "group": {
    "long": {
      "Computers": 121222.53,
      "Others": 5624.600040692091,
      "Semiconductors": 115792.2,
      "Auto Manufacturers": 22453.78620745659,
      "Banks": 2503.3599999999997,
      "Miscellaneous Manufactur": 43077.12,
      "Internet": 5126.98,
      "Beverages": 651.35,
      "Pharmaceuticals": 16.42578845143318
    },
    "short": {
      "Others": -30.0
    }
  }
}
```
