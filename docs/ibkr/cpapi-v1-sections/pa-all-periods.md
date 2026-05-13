### All Periods Copy Location

Returns the performance across all available time periods for the given accounts, if more than one account is passed, the result is consolidated.

`POST /pa/allperiods`

#### Request Object

###### Body Parameters

**acctIds:** Array of Strings. Required  
 Include each account ID to receive data for.

- Python
- cURL

```
request_url = f"{baseUrl}/pa/performance"
json_content = {
  "acctIds": ["U1234567"]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
{{baseUrl}}/pa/allperiods\
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "acctIds": ["U1234567", "U4567890"]}'
```

#### Response Object

**currencyType:** String.  
 Confirms the currency type.  
 If trading exclusively in your base currency, “base” will be returned.

**rc:** int.  
 Returns the data identifier (Client Portal Only).

**view:** Array of Strings.  
 Returns the accounts included in the response.

**nd:** int.  
 Returns the total data points.

**id:** String.  
 Returns the request identifier.  
 Internal use only.

**included:** Array of Strings.  
 Returns the accounts included in the response.

**pm:** String.  
 Portfolio Measure. Used to indicate TWR or MWR values returned.

**{AccountID}:** Object.  
 Returns the account identifier for the referenced object.

**{Period Value}:** Object.  
 Designates the period the data covers.  
 Potential Values: “1D”,”7D”,”MTD”,”1M”,”YTD”,”1Y”  
 {  
 **nav:** Object.  
 Net asset value data for the account or consolidated accounts. NAV data is not applicable to benchmarks.

**cps:** Array of Integers.  
 Returns an array containing Cumulative performance data over the period.

**freq:** String.  
 Displays the values corresponding to a given frequency.

**dates:** Array of Strings.  
 Returns the array of dates corresponding to your frequency, the length should be same as the length of returns inside data.

**startNAV:** Object.  
 Returns the intiial NAV available.  
 {  
 **date:** String.  
 Returns the starting date for the request.

**val:** int.  
 Returns the Net Asset Value of the account.  
 }  
 }

**periods:** String.  
 Returns the period ranges included in the response.

**start:** String.  
 Returns the starting value of the value range.

**end:** String.  
 Returns the end of the available frequency.

**baseCurrency:** String.  
 Returns the base currency used in the account.

```
{
    "currencyType": "base",
    "rc": 0,
    "view": [
        "U1234567"
    ],
    "nd": 366,
    "id": "getPerformanceAllPeriods",
    "included": [
        "U1234567"
    ],
    "pm": "TWR",
    "U1234567": {
        "1D": {
            "nav": [
                3666392.5393
            ],
            "cps": [
                0.0005
            ],
            "freq": "D",
            "dates": [
                "20250603"
            ],
            "startNAV": {
                "date": "20250602",
                "val": 3664681.7504
            }
        },
        "lastSuccessfulUpdate": "2025-06-03 15:22:03",
        "start": "20240603",
        "YTD": {
            "nav": [
                3674381.3273,
                ...,
                3666392.5393
            ],
            "cps": [
                0,
                -0.0061,
                ...,
                -0.0021
            ],
            "freq": "D",
            "dates": [
                "20250101",
                ...,
                "20250603"
            ],
            "startNAV": {
                "date": "20241231",
                "val": 3674236.8245
            }
        },
        "1Y": {
            "nav": [
                3072764.5772,
                ...,
                3666392.5393
            ],
            "cps": [
                0.0054,
                ...,
                0.1996
            ],
            "freq": "D",
            "dates": [
                "20240603",
                ...,
                "20250603"
            ],
            "startNAV": {
                "date": "20240531",
                "val": 3056403.4525
            }
        },
        "periods": [
            "1D",
            "7D",
            "MTD",
            "1M",
            "YTD",
            "1Y"
        ],
        "end": "20250603",
        "MTD": {
            "nav": [
                3664681.7504,
                3666392.5393
            ],
            "cps": [
                0.003,
                0.0035
            ],
            "freq": "D",
            "dates": [
                "20250602",
                "20250603"
            ],
            "startNAV": {
                "date": "20250530",
                "val": 3653634.7799
            }
        },
        "1M": {
            "nav": [
                3626879.8271,
                ...,
                3666392.5393
            ],
            "cps": [
                -0.0046,
                ...,
                0.0063
            ],
            "freq": "D",
            "dates": [
                "20250505",
                ...,
                "20250603"
            ],
            "startNAV": {
                "date": "20250502",
                "val": 3643556.8781
            }
        },
        "7D": {
            "nav": [
                3649592.4093,
                ...,
                3666392.5393
            ],
            "cps": [
                -0.0005,
                ...,
                0.0041
            ],
            "freq": "D",
            "dates": [
                "20250528",
                ...,
                "20250603"
            ],
            "startNAV": {
                "date": "20250527",
                "val": 3651501.5873
            }
        },
        "baseCurrency": "USD"
    }
}
```
