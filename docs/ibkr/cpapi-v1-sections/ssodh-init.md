### Initialize Brokerage Session Copy Location

This is essential for using all endpoints besides /portfolio, including access to trading and market data.

`POST /iserver/auth/ssodh/init`

#### Request Object

###### Body Params

**publish:** Boolean. Required  
 Determines if the request should be sent immediately.  
 Users should always pass true. Otherwise, a ‘500’ response will be returned.

**compete:** Boolean. Required  
 Determines if other brokerage sessions should be disconnected to prioritize this connection.

- Python
- cURL

```
request_url = "{baseUrl}/iserver/auth/ssodh/init"
json_content= {"publish":True,"compete":True}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/auth/ssodh/init \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "publish":true,
  "compete":true
}'
```

#### Response Object

**authenticated:** bool.  
 Returns whether your brokerage session is authenticated or not.

**competing:** bool.  
 Returns whether you have a competing brokerage session in another connection.

**connected:** bool.  
 Returns whether you are connected to the gateway, authenticated or not.

**message:** String.  
 If there is a message about your authenticate status, it will be returned here.  
 Authenticated sessions return an empty string.

**MAC:** String.  
 IBKR MAC information. Internal use only.

**serverInfo:** Object.

**serverName:** String.  
 IBKR server information. Internal use only.

**serverVersion:** String.  
 IBKR version information. Internal use only.

```
{
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
```
