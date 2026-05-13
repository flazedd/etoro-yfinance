### Currency Pairs Copy Location

Obtains available currency pairs corresponding to the given target currency.

`GET /iserver/currency/pairs`

#### Request Object

###### Query Params

**currency:** String. Required  
 Specify the target currency you would like to receive official pairs of.  
 Valid Structure: “USD”

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/currency/pairs?currency=USD"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/currency/pairs?currency=USD \
--request GET
```

#### Response Object

**{{currency}}:** List of Objects.  
 [{  
 **symbol:** String.  
 The official symbol of the given currency pair.

**conid:** int.  
 The official contract identifier of the given currency pair.

**ccyPair:** String.  
 Returns the counterpart of  
 }]

```
{
  "USD": [
    {
      "symbol": "USD.SGD",
      "conid": 37928772,
      "ccyPair": "SGD"
    },
	{...},
    {
      "symbol": "USD.RUB",
      "conid": 28454968,
      "ccyPair": "RUB"
    }
  ]
}
```
