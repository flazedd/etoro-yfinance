### Re-authenticate the Brokerage Session (Deprecated) Copy Location

When using the CP Gateway, this endpoint provides a way to reauthenticate to the Brokerage system as long as there is a valid brokerage session.

All interest in reauthenticating the gateway session should be handled using the [/iserver/auth/ssodh/init](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi/#ssodh-init) endpoint.

`POST /iserver/reauthenticate`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/reauthenticate"
json_content = {}
requests.post(url=request_url, json=json_content )
```

```
curl \
--url {{baseUrl}}/iserver/reauthenticate \ 
--request POST \ 
--header 'Content-Type:application/json' \ 
--data '{}'
```

#### Response Object

**message:** String.  
 Returns “triggered” to indicate the response was sent.

```
{
  "message": "triggered"
}
```
