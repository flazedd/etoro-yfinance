### Delete an alert Copy Location

Permanently delete an existing alert.

If alertId is 0, it will delete all alerts

If you call delete an MTA alert, it will reset to the default state.

`DELETE /iserver/account/{{ accountId }}/alert/{{ alertId }}`

#### Request Parameters

###### Path Parameters

**accountId:** *String*. Required  
 Identifier for the unique account to retrieve information from.  
 Value Format: “DU1234567”

**alertId:** *int***.** Required  
 order\_id returned from the original alert creation, or from the list of available alerts.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/U1234567/alert/9876543210"
json_content = {}
requests.delete(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account/U1234567/alert/9876543210 \
--request DELETE
```

#### Response Object

**request\_id:** *int*.  
 Returns ‘null’

**order\_id:** *int*.  
 Returns requested alertId or order\_id

**success:** *bool*.  
 Returns true if successful

**text:** *String*.  
 Adds additional information for “success” status.

**failure\_list:** *String*.  
 If “success” returns false, will list failed order Ids

```
{
  "request_id": null,
  "order_id": 9876543210,
  "success": true,
  "text": "Request was submitted",
  "failure_list": null
}
```
