### Unread Bulletins Copy Location

Returns the total number of unread fyis

`GET /fyi/unreadnumber`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/fyi/unreadnumber"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/fyi/unreadnumber \
--request GET
```

#### Response Object

**BN:** int.  
 Returns the number of unread bulletins.

```
{
  "BN": 4
}
```
