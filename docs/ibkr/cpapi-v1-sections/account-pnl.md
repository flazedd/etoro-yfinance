### Account Profit and Loss Copy Location

Returns an object containing PnL for the selected account and its models (if any).

`GET /iserver/account/pnl/partitioned`

#### Request Object:

No additional parameters necessary.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/pnl/partitioned"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/account/pnl/partitioned \
--request GET
```

#### Response Object:

**upnl** : JSON Object.

Refers to “updated PnL”. Holds a json object of key-value paired account pnl details.

**{accountId}.Core:** JSON Object.

An object based on your current account or group model.

**rowType:** int.  
 Returns the positional value of the returned account. Always returns 1 for individual accounts.

**dpl:** float.  
 Daily PnL for the specified account profile.

**nl:** float.  
 Net Liquidity for the specified account profile.

**upl:** float.  
 Unrealized PnL for the specified account profile.

**el:** float.  
 Excess Liquidity for the specified account profile.

**mv:** float.  
 Margin value for the specified account profile.

```
{
  "upnl": {
    "U1234567.Core": {
      "rowType": 1,
      "dpl": 15.7,
      "nl": 10000.0,
      "upl": 607.0,
      "el": 10000.0,
      "mv": 0.0
    }
  }
}
```
