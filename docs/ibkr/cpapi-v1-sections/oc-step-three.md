### Step Three: Validate The Contract Copy Location

After calling the /search and /strikes endpoints, users can use the [/iserver/secdef/info endpoint](/campus/ibkr-api-page/cpapi-v1/#secdef-info-contract) to validate the derivative conId. This endpoint should be called for each strike and right combination of interest.

Note: For Futures Options, the conId of the Index should be specified, along with the explicit exchange being listed. As an example, CL futures options should specify “exchange=NYMEX” as an additional query parameter.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/secdef/info?conid=416904&secType=OPT&month=JAN25&strike=3975&right=P
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/secdef/info?conid=416904&secType=OPT&month=JAN25&strike=3975&right=P \
--request GET
```

While all of the information is relevant, it is most important to save the conId in order to track the contract itself. For the lifespan of the Option, this conId will remain constant. This will also be used for all subsequent requests for market data or order placement.

```
[
  {
    "conid": 654371995,
    "symbol": "SPX",
    "secType": "OPT",
    "exchange": "SMART",
    "listingExchange": null,
    "right": "P",
    "strike": 3975.0,
    "currency": "USD",
    "cusip": null,
    "coupon": "No Coupon",
    "desc1": "SPX",
    "desc2": "JAN 16 '25 3975 Put (AM)",
    "maturityDate": "20250116",
    "multiplier": "100",
    "tradingClass": "SPX",
    "validExchanges": "SMART,CBOE,IBUSOPT"
  }
]
```
