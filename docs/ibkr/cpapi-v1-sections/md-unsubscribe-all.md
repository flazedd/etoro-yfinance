### Unsubscribe (All) Copy Location

Cancel all market data request(s). To cancel market data for a specific conid, see /iserver/marketdata/{conid}/unsubscribe.

```
GET /iserver/marketdata/unsubscribeall
```

#### Request Object

No params or arguments should be passed.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/marketdata/unsubscribeall"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/marketdata/unsubscribeall \ 
--request GET
```

#### Response Object

**confirmed:** String.  
 Returns a confirmation status of your unsubscribe request.

```
{
  "unsubscribed": true
}
```
