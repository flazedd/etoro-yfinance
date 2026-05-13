### Suppress Messages Copy Location

Disables a messageId, or series of messageIds, that will no longer prompt the user.

`POST /iserver/questions/suppress`

#### Request Object

###### Body Param

**messageIds:** Array of Strings.  
 The identifier for each warning message to suppress.  
 The array supports up to 51 messages sent in a single request. Any additional values will result in a system error.  
 The only supported message IDs are listed in our [Suppressible Message IDs](/campus/ibkr-api-page/cpapi-v1/#suppressible-id) list. However, users should look to suppress messages on an as-needed basis to avoid unexpected order submissions.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/questions/suppress"
json_content = {
  "messageIds": ["o102"]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/questions/suppress \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "messageIds": ["o102"]
}'
```

#### Response Object

**status:** String.  
 Verifies that the request has been sent.

```
{
  "status": "submitted"
}
```
