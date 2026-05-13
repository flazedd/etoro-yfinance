### Security Stocks by Symbol Copy Location

Returns an object contains all stock contracts for given symbol(s)

`GET /trsrv/stocks`

#### Request Object

###### Query Params

**symbols**: String.  
 Comma-separated list of stock symbols. Symbols must contain only capitalized letters.

- Python
- cURL

```
request_url = f"{baseUrl}/trsrv/stocks?symbols=AAPL,IBKR"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/trsrv/stocks?symbols=AAPL,IBKR\
--request GET
```

#### Response Object

**symbol:** Array of Json  
 Contains a series of Json for all contracts that match the symbol.

**name:** String.  
 Full company name for the given contract.

**chineseName:** String.  
 Chinese name for the given company.

**assetClass:** String.  
 Asset class for the given company.

**contracts:** Array.  
 A series of arrays pertaining to the same company listed by “name”.  
 Typically differentiated based on currency of the primary exchange.

**conid:** int.  
 Contract ID for the specific contract.

**exchange:** String.  
 Primary exchange for the given contract.

**isUS:** bool.  
 States whether the contract is hosted in the United States or not.

```
{
  "AAPL": [
    {
      "name": "APPLE INC",
      "chineseName": "苹果公司",
      "assetClass": "STK",
      "contracts": [
        {
          "conid": 265598,
          "exchange": "NASDAQ",
          "isUS": true
        },
        {
          "conid": 38708077,
          "exchange": "MEXI",
          "isUS": false
        },
        {
          "conid": 273982664,
          "exchange": "EBS",
          "isUS": false
        }
      ]
    },
    {
      "name": "LS 1X AAPL",
      "chineseName": null,
      "assetClass": "STK",
      "contracts": [
        {
          "conid": 493546048,
          "exchange": "LSEETF",
          "isUS": false
        }
      ]
    },
    {
      "name": "APPLE INC-CDR",
      "chineseName": "苹果公司",
      "assetClass": "STK",
      "contracts": [
        {
          "conid": 532640894,
          "exchange": "AEQLIT",
          "isUS": false
        }
      ]
    }
  ]
}
```
