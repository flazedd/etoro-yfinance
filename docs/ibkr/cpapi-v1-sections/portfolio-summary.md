### Portfolio Summary Copy Location

Information regarding settled cash, cash balances, etc. in the account’s base currency and any other cash balances hold in other currencies. /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint. The list of supported currencies is available at https://www.interactivebrokers.com/en/index.php?f=3185.

`GET /portfolio/{accountId}/summary`

#### Request Object

###### Path Params

**accountId:** String. Required  
 Specify the account ID for which account you require ledger information on.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/U1234567/summary"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/U1234567/summary \
--request GET
```

#### Response Object

The /summary endpoint returns a Key: Value Object structure. This returns a total of 45-135 unique values used to summarize the account.

Responses will come as the base value, containing a summary of all returned details, followed by an identical response name with a trailing “-c” or “-s”. “-c” represents commodity values held under the account. Meanwhile, “-s” represents all security values held on the account.

**{object key}:** Object.  
 This key indicates what data is being returned. This may include account information, balance information, or other relevant portfolio details as specified.

**amount:** float.  
 Returns the price value regarding the key.  
 May return null if price value not required.

**currency:** String.  
 Returns the base currency the response is built with.

**isNull:** bool.  
 Returns if the value is unavailable.

**timestamp:** int.  
 Returns the time the data was retrieved in epoch time.

**value:** String.  
 Returns a string details about the given key.  
 May return null if no string value required.

**severity:** int.  
 Internal use only.

```
{
  "accountcode": {
    "amount": 0.0,
    "currency": null,
    "isNull": false,
    "timestamp": 1702582422000,
    "value": "U1234567",
    "severity": 0
  },
  {...},
  "indianstockhaircut": {
    "amount": 0.0,
    "currency": "USD",
    "isNone": false,
    "timestamp": 1702582422000,
    "value": null,
    "severity": 0
  }
}
```
