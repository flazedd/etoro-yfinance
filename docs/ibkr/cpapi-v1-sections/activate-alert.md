### Activate or deactivate an alert Copy Location

Activate or Deactivate existing alerts created for this account. This does not delete alerts, but disables notifications until reactivated.

`POST /iserver/account/{{ accountId }}/alert/activate`

#### Request Details

###### Path Parameters

**accountId:** *String*. Required  
 Identifier for the unique account to retrieve information from.  
 Value Format: “DU1234567”

###### Request Body

**alertId**: *int.* Required  
 The alertId, or order\_id, received from order creation or the list of alerts.

**alertActive**: *int.* Required  
 Set whether or not the alert should be active (1) or inactive (0)

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/U1234567/alert/activate"
--request POST \
--header 'Content-Type:application/json' \
--data '{
    "alertId": 9876543210,
    "alertActive": 1
}'
```

```
curl \
--url {{baseUrl}}/iserver/account/U1234567/alert/activate \
--request POST \
--header 'Content-Type:application/json' \
--data '{
    "alertId": 9876543210,
    "alertActive": 1
}'
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
