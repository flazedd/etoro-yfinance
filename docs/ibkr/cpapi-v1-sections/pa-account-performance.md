### Account Performance Copy Location

Returns the performance (MTM) for the given accounts, if more than one account is passed, the result is consolidated.

`POST /pa/performance`

#### Request Object

###### Body Parameters

**acctIds:** Array of Strings. Required  
 Include each account ID to receive data for.

**period:** String. Required  
 Specify the period for which the account should be analyzed.  
 Available Values: “1D”,”7D”,”MTD”,”1M”,”YTD”,”1Y”

- Python
- cURL

```
request_url = f"{baseUrl}/pa/performance"
json_content = {
  "acctIds": ["U1234567"]
  "period": "1D"
}
requests.post(url=request_url, json=json_content)
```

```
curl \
{{baseUrl}}/pa/performance \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "acctIds": ["U1234567", "U4567890"]
  "period": "1D"
}'
```

#### Response Object

**currencyType:** String.  
 Confirms if the currency type.  
 If trading primarily in your base currency, “base” will be returned.

**rc:** int.  
 Returns the data identifier (Client Portal Only).

**nav:** Object.  
 Net asset value data for the account or consolidated accounts. NAV data is not applicable to benchmarks.

**data:** Array of Object.  
 Contains the affiliated ‘nav’ data.

**idType:** String.  
 Returns how identifiers are determined.

**navs:** int.  
 Returns the series of data points corresponding to the listed days.

**start:** String.  
 Returns the first available date for data.

**end:** String.  
 Returns the end of the available frequency.

**id:** String.  
 Returns the account identifier.

**startNAV:** Object.  
 Returns the intiial NAV available.

**date:** String.  
 Returns the starting date for the request.

**val:** int.  
 Returns the Net Asset Value of the account.

**baseCurrency:** String.  
 Returns the base currency used in the account.

**freq:** String.  
 Displays the values corresponding to a given frequency.

**dates:** Array of Strings.  
 Returns the array of dates corresponding to your frequency, the length should be same as the length of returns inside data.

**nd:** int.  
 Returns the total data points.

**cps:** object.  
 Returns the object containing the Cumulative performance data.

**data:** Array of Objects.  
 Returns the array of cps data available.

**idType:** String.  
 Returns the key value of the request.

**start:** String.  
 Returns the starting value of the value range.

**end:** String.  
 Returns the ending value of the value range.

**returns:** Array of ints.  
 Returns all cps values in order between the start and end times.

**id:** String.  
 Returns the account identifier.

**baseCurrency:** String.  
 Returns the base curency for the account.

**freq:** String.  
 Returns the determining frequency of the data range.

**dates:** Array of Strings.  
 Returns the dates corresponding to the frequency of data.

**tpps:** Object.  
 Returns the Time period performance data.

**data:** Array.  
 Object containing all data about tpps.

**idType:** String.  
 Returns the key value of the request.

**start:** String.  
 Returns the starting value of the value range.

**end:** String.  
 Returns the ending value of the value range.

**returns:** Array of ints.  
 Returns all cps values in order between the start and end times.

**id:** String.  
 Returns the account identifier.

**baseCurrency:** String.  
 Returns the base curency for the account.

**freq:** String.  
 Returns the determining frequency of the data range.

**dates:** Array of Strings.  
 Returns the dates corresponding to the frequency of data.

**id:** String.  
 Returns the request identifier, getPerformanceData.

**included:** Array.  
 Returns an array contianing accounts reviewed.

**pm:** String.  
 Portfolio Measure. Used to indicate TWR or MWR values returned.

```
{
  "currencyType": "base",
  "rc": 0,
  "nav": {
    "data": [
      {
        "idType": "acctid",
        "navs": [
          2.027673321223E8,
          {...},
          2.157185988239E8
        ],
        "start": "20230102",
        "end": "20231213",
        "id": "U1234567",
        "startNAV": {
          "date": "20221230",
          "val": 2.027677613449E8
        },
        "baseCurrency": "USD"
      }
    ],
    "freq": "D",
    "dates": [
      "20230102",
          {...},
      "20231213"
    ]
  },
  "nd": 346,
  "cps": {
    "data": [
      {
        "idType": "acctid",
        "start": "20230102",
        "end": "20231213",
        "returns": [
          0,
          {...},
          0.0639
        ],
        "id": "U1234567",
        "baseCurrency": "USD"
      }
    ],
    "freq": "D",
    "dates": [
      "20230102",
          {...},
      "20231213"
    ]
  },
  "tpps": {
    "data": [
      {
        "idType": "acctid",
        "start": "20230102",
        "end": "20231213",
        "returns": [
          0.0037,
          0.0031,
          0.0033,
          0.0034,
          0.02,
          0.0127,
          0.0036,
          0.0036,
          0.0034,
          0.0012,
          0.0026,
          0.0017
        ],
        "id": "U1234567",
        "baseCurrency": "USD"
      }
    ],
    "freq": "M",
    "dates": [
      "202301",
      "202302",
      "202303",
      "202304",
      "202305",
      "202306",
      "202307",
      "202308",
      "202309",
      "202310",
      "202311",
      "202312"
    ]
  },
  "id": "getPerformanceData",
  "included": [
    "U1234567"
  ],
  "pm": "TWR"
}
```
