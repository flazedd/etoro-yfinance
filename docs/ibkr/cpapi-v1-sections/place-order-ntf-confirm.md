### Respond to a Server Prompt Copy Location

Respond to a server prompt received via ntf webscoket message.

`POST /iserver/notification`

#### Request Object

###### Body Params

**orderId** int. Required  
 IB-assigned order identifier obtained from the ntf websocket message that delivered the server prompt.

**reqId** string. Required  
 IB-assigned request identifier obtained from the ntf websocket message that delivered the server prompt.

**text** string. Required  
 The selected value from the “options” array delivered in the server prompt ntf websocket message.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/notification"
json_content = {
  "orderId": 987654321,
  "reqId": "12345",
  "text": "Yes"
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {baseUrl}/iserver/notification \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "orderId": 987654321,
  "reqId": "12345",
  "text": "Yes"
}'
```

#### Response Object

**{Status text}:** string  
 Returns the status of the confirmation message.

```
Success
```
