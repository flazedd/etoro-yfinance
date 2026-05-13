### All Conids by Exchange Copy Location

Send out a request to retrieve all contracts made available on a requested exchange. This returns all contracts that are tradable on the exchange, even those that are not using the exchange as their primary listing.

**Note:** This is only available for Stock contracts.

`GET /trsrv/all-conids`

#### Request Object

###### Query Params

**exchange:** String. Required  
 Specify a single exchange to receive conids for.

- Python
- cURL

```
request_url = f"{baseUrl}/trsrv/all-conids?exchange=AMEX"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/trsrv/all-conids?exchange=AMEX \
--request GET
```

#### Response Object

**ticker:** String.  
 Returns the ticker symbol of the contract

**conid:** int.  
 Returns the contract identifier of the returned contract.

**exchange:** String.  
 Returns the exchanger of the returned contract.

```
[
  {
    "ticker": "BMO",
    "conid": 5094,
    "exchange": "NYSE"
  },
  {...},
  {
    "ticker": "ZKH",
    "conid": 671347171,
    "exchange": "NYSE"
  }
]
```
