### Reset Suppressed Messages Copy Location

Resets all messages disabled by the [Suppress Messages endpoint](/campus/ibkr-api-page/cpapi-v1/#questions-suppress).

`POST /iserver/questions/suppress/reset`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/questions/suppress/reset"
json_content = {}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/questions/suppress/reset \
--request POST \
--header 'Content-Type:application/json' \
--data ''
```

#### Response Object

**status:** String.  
 Verifies that the request has been sent.

```
{
  "status": "submitted"
}
```
