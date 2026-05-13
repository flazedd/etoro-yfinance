### Ping the server Copy Location

If the gateway has not received any requests for several minutes an open session will automatically timeout. The tickle endpoint pings the server to prevent the session from ending. It is expected to call this endpoint approximately every 60 seconds to maintain the connection to the brokerage session.

`POST /tickle`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/tickle"
json_content = {}
requests.post(url=request_url, json=json_content)
```

```
curl \ 
--url {{baseUrl}}/tickle \
--request POST \
--header 'Content-Type:application/json' \
--data '{}'
```

#### Response Object

**session:** String.  
 Returns the session identifier of your connection.  
 Can be used for the cookie parameter of your request.

**ssoExpires:** int.  
 Displays the time until session expiry in milliseconds.

**collission:** bool.  
 Internal use only.

**userId:** int.  
 Internal use only.

**hmds:** object.  
 Returns any potential historical data-specific information.  
 “No bridge” indicates historical data is not being currently requested.

**iserver:** object.  
 Returns the content of the [/iserver/auth/status](#auth-status) endpoint.

```
{
  "session": "bb665d0f55b6289d70bc7380089fc96f",
  "ssoExpires": 460311,
  "collission": false,
  "userId": 123456789,
  "hmds": {
    "error": "no bridge"
  },
  "iserver": {
    "authStatus": {
      "authenticated": true,
      "competing": false,
      "connected": true,
      "message": "",
      "MAC": "98:F2:B3:23:BF:A0",
      "serverInfo": {
        "serverName": "JifN19053",
        "serverVersion": "Build 10.25.0p, Dec 5, 2023 5:48:12 PM"
      }
    }
  }
}
```
