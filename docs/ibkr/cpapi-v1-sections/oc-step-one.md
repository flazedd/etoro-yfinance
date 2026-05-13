### Step One: Instantiate the Option Chain Copy Location

To begin, users must first make a call to the [/iserver/secdef/search endpoint](/campus/ibkr-api-page/cpapi-v1/#search-symbol-contract) for the underlying symbol. This is required for all future steps every time the user does not know the final derivative’s conId.

**This must always be called before proceeding, even if you are aware of the conId and expiration dates.**

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/secdef/search?symbol=SPX"
requests.get(url=request_url)
```

```
curl --insecure \
--url https://localhost:5000/v1/api/iserver/secdef/search?symbol=SPX \
--request GET
```

In the response, we are able to see two important values returned. The first, we can find our ConID for the underlying, 416904. We will need this for our future requests.

We can also see under “sections”::”secType”:”OPT, “months” we will see all of the contract expirations months. This will be required to build our option chain in the next request.

```
[
  {
    "conid": "416904",
    "companyHeader": "S&P 500 Stock Index - CBOE",
    "companyName": "S&P 500 Stock Index",
    "symbol": "SPX",
    "description": "CBOE",
    "restricted": "IND",
    "sections": [
      {...},
      {
        "secType": "OPT",
        "months": "JAN24;FEB24;MAR24;APR24;MAY24;JUN24;JUL24;AUG24;SEP24;OCT24;NOV24;DEC24;JAN25;MAR25;JUN25;DEC25;DEC26;DEC27;DEC28;DEC29",
        "exchange": "SMART;CBOE;IBUSOPT"
      },
      {...}
    ]
  }
]
```
