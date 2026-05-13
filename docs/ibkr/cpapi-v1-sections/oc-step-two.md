### Step Two: Find Potential Strikes Copy Location

After querying the /iserver/secdef/search endpoint, developers should now call the [/iserver/secdef/strikes endpoint](/campus/ibkr-api-page/cpapi-v1/#strike-conid-contract). To receive the appropriate strikes, the conId, secType, and expiration month should be specified.

**This must always be called before proceeding, even if you are aware of the strikes.**

Notes:

- For Futures Options, the conId of the Index should be specified, along with the explicit exchange being listed. As an example, CL futures options should specify “exchange=NYMEX” as an additional query parameter.
- The inclusion of the name field will prohibit the /iserver/secdef/strikes endpoint from returning data. After retrieving your expected contract, customers looking to create option chains should remove the name field from the request.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/secdef/strikes?conid=416904&sectype=OPT&month=JAN25"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/secdef/strikes?conid=416904&secType=OPT&month=JAN25 \
--request GET
```

As a response, an object containing arrays of all Call and Put strikes will be returned. This will only return potential strike prices. This does not necessarily indicate. These strikes should be confirmed with our /info endpoint to confirm if the strike is valid.

Note:

- This endpoint will always return empty arrays unless [/iserver/secdef/search](/campus/ibkr-api-page/cpapi-v1/#search-symbol-contract) is called for the same underlying symbol beforehand. The inclusion of the name field with the [/iserver/secdef/search](/campus/ibkr-api-page/cpapi-v1/#search-symbol-contract) endpoint will prohibit the strikes endpoint from returning data. After retrieving your expected contract from the initial search, developers looking to create option chains should remove the name field from the request.

```
{
  "call": [
    200.0,
  {...},
    7800.0
  ],
  "put": [
    200.0,
  {...},
    7800.0
  ]
}
```
