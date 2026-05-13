### Logout of the current session Copy Location

Logs the user out of the gateway session. Any further activity requires re-authentication.

`POST /logout`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = "{baseUrl}/logout"
json_content= {}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/logout \
--request POST \
--header 'Content-Type:application/json' \
--data '{}'
```

#### Response Object

**status:** bool.  
 Returns true if the session was ended.

```
{
  "status":true
}
```
