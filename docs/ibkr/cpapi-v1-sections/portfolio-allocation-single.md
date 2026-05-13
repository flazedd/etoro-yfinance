### Portfolio Allocation (Single) Copy Location

Information about the account’s portfolio allocation by Asset Class, Industry and Category. /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint.

`GET /portfolio/{accountId}/allocation`

#### Request Object

###### Path Params

**accountId:** String. Required  
 Specify the account ID for the request.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/U1234567/allocation"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/U1234567/allocation \
--request GET
```

#### Response Object

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
      "STK": 317071.39468663215,
      "CASH": 2.1510110008312488E8
    },
    "short": {
      "OPT": -30.0,
      "CASH": -25.917167515158653
    }
  },
  "sector": {
    "long": {
      "Others": 5628.650040692091,
      "Technology": 237511.16,
      "Industrial": 43134.63,
      "Consumer, Cyclical": 22537.62620745659,
      "Financial": 2504.35,
      "Communications": 5116.61,
      "Consumer, Non-cyclical": 665.4884384834767
    },
    "short": {
      "Others": -30.0
    }
  },
  "group": {
    "long": {
      "Computers": 121517.38,
      "Others": 5628.650040692091,
      "Semiconductors": 115993.78,
      "Auto Manufacturers": 22537.62620745659,
      "Banks": 2504.35,
      "Miscellaneous Manufactur": 43134.63,
      "Internet": 5116.61,
      "Beverages": 649.07,
      "Pharmaceuticals": 16.41843848347664
    },
    "short": {
      "Others": -30.0
    }
  }
}
```
