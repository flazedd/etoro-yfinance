### Authentication Status Copy Location

Current Authentication status to the Brokerage system. Market Data and Trading is not possible if not authenticated, e.g. authenticated shows false

`POST /iserver/auth/status`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/auth/status"
json_content = {}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/auth/status \
--request POST \
--header 'Content-Type:application/json' \
--data '{}'
```

#### Response Object

**authenticated:** bool.  
 Returns whether your brokerage session is authenticated or not.

**competing:** bool.  
 Returns whether you have a competing brokerage session in another connection.

**connected:** bool.  
 Returns whether you are connected to the gateway, authenticated or not.

**message:** String.  
 If there is a message about your authenticate status, it will be returned here.  
 Authenticated sessions return an empty string.

**MAC:** String.  
 IBKR MAC information. Internal use only.

**serverInfo:** Object.

**serverName:** String.  
 IBKR server information. Internal use only.

**serverVersion:** String.  
 IBKR version information. Internal use only.

**hardware\_info:** String.  
 IBKR version information. Internal use only.

**fail:** String.  
 Returns the reason for failing to retrieve authentication status.

```
{
  "authenticated": true,
  "competing": false,
  "connected": true,
  "message": "",
  "MAC": "12:B:B3:23:BF:A0",
  "serverInfo": {
    "serverName": "JifN19053",
    "serverVersion": "Build 10.25.0p, Dec 5, 2023 5:48:12 PM"
  },
  "hardware_info": "3b0679ee|98:A2:B3:23:BC:A0",
  "fail": ""
}
```

#### Alternate Response Object

Users that have been timed out or logged out of their session will result in a “false” authentication status, indicating the user is not maintaining a brokerage session.

```
{
  "authenticated": false,
  "competing": false,
  "connected": false,
  "MAC": "98:B2:C3:45:DE:F6"
}
```
