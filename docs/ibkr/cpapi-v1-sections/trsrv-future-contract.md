### Security Future by Symbol Copy Location

Returns a list of non-expired future contracts for given symbol(s)

`GET /trsrv/futures`

#### Request Object

###### Query Params

**symbols**: *String*. Required  
 Indicate the symbol(s) of the underlier you are trying to retrieve futures on. Accepts comma delimited string of symbols.

- Python
- cURL

```
request_url = f"{baseUrl}/trsrv/futures?symbols=ES,MES"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/trsrv/futures?symbols=ES,MES \
--request GET
```

#### Response Body

**symbol:** Array  
 Displayed as the string of your symbol  
 Contains a series of objects for each symbol that matches the requested.

**symbol:** String.  
 The requested symbol value.

**conid:** int.  
 Contract identifier for the specific symbol

**underlyingConid:** int.  
 Contract identifier for the future’s underlying contract.

**expirationDate:** int.  
 Expiration date of the specific future contract.

**ltd:** int.  
 Last trade date of the future contract.

**shortFuturesCutOff:** int.  
 Represents the final day for contract rollover for shorted futures.

**longFuturesCutOff:** int.  
 Represents the final day for contract rollover for long futures.

```
{
  "ES": [
    {
      "symbol": "ES",
      "conid": 495512552,
      "underlyingConid": 11004968,
      "expirationDate": 20231215,
      "ltd": 20231214,
      "shortFuturesCutOff": 20231214,
      "longFuturesCutOff": 20231214
    },
    {...}
  ],
  "MES": [
    {
      "symbol": "MES",
      "conid": 586139726,
      "underlyingConid": 362673777,
      "expirationDate": 20231215,
      "ltd": 20231215,
      "shortFuturesCutOff": 20231215,
      "longFuturesCutOff": 20231215
    },
    {...}
  ]
}
```
