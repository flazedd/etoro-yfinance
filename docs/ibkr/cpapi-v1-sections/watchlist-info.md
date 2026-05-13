### Get Watchlist Information Copy Location

Request the contracts listed in a particular watchlist.

`GET /iserver/watchlist`

#### Request Object

###### Query Params

**id:** String. Required  
 Set equal to the watchlist ID you would like data for.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/watchlist?id=1234"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/watchlist?id=1234 \
--request GET
```

#### Response Object

The first request may only return the values C, conid, and name values. Subsequent requests will add additional contract information.

**id:** String.

**hash:** String.

**name:** String.

**readOnly:** bool.

**instruments:** Array of Objects.  
 [{  
 **C:** String.  
 Returns the contract ID.

**conid:** int.  
 Returns the contract ID.

**name:** String.  
 Returns the long name of the company.

**fullName:** String.  
 Returns the local symbol of the contract.

**assetClass:** String.  
 Returns the security type of the contract.

**ticker:** String.  
 Returns the ticker symbol for the contract.

**chineseName:** String.  
 Returns the Chinese character name for the contract.  
 }]

```
{
  "id": "1234",
  "hash": "1702581306241",
  "name": "Test Watchlist",
  "readOnly": false,
  "instruments": [
    {
      "ST": "STK",
      "C": "8314",
      "conid": 8314,
      "name": "INTL BUSINESS MACHINES CORP",
      "fullName": "IBM",
      "assetClass": "STK",
      "ticker": "IBM",
      "chineseName": "国际商业机器"
    },
    {
      "ST": "STK",
      "C": "8894",
      "conid": 8894,
      "name": "COCA-COLA CO/THE",
      "fullName": "KO",
      "assetClass": "STK",
      "ticker": "KO",
      "chineseName": "可口可乐"
    }
  ]
}
```
