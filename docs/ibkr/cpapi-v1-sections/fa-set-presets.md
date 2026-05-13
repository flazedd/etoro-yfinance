### Set Allocation Presets Copy Location

Set the preset behavior for allocation groups for specific events.

`POST /iserver/account/allocation/presets`

#### Request Object

###### Body Params

**default\_method\_for\_all:** String. Required  
 Set the default allocation method to be used for all allocation groups without a set value.

**group\_auto\_close\_positions:** bool. Required

**profiles\_auto\_close\_positions:** bool. Required

**strict\_credit\_check:** bool. Required

**group\_proportional\_allocation:** bool. Required

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/allocation/presets" 
json_content = {
  "default_method_for_all": "E",
  "group_auto_close_positions": true,
  "profiles_auto_close_positions": true,
  "strict_credit_check": false,
  "group_proportional_allocation": false
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account/allocation/presets \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "default_method_for_all": "E",
  "group_auto_close_positions": true,
  "profiles_auto_close_positions": true,
  "strict_credit_check": false,
  "group_proportional_allocation": false
}'
```

#### Response Object

**success:** bool.  
 Confirms that the preset was properly set.

```
{
  "success": true
}
```
