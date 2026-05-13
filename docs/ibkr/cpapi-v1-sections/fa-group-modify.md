### Modify Allocation Group Copy Location

Modify an existing allocation group.

`PUT /iserver/account/allocation/group`

#### Request Object

###### Body Params

**name:** String. Required Required  
 Name used to refer to your allocation group. If prev\_name is specified, this will become the new name of the group.

**prev\_name:** String.  
 Name used to refer to your existing allocation group.  
 Only use this when updating the group name.

**accounts:** Array of objects. Required  
 Contains a series of objects depicting which accounts are involved and, for user-defined allocation methods, the distribution value for each sub-account.  
 [{  
 **name:** String. Required  
 The accountId of a given sub-account.  
 Value Format: “U1234567”

**amount:** Number.  
 The total distribution value for each sub-account for user-defined allocation methods.  
 }]  
 **default\_method:** String. Required  
 Specify the allocation method code for the allocation group.  
 See Allocation Method Codes for more details.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/allocation/group"
json_content = {
  "name":"Group_1_NetLiq",
  "accounts":[{
    "name":"U1234567",
    "amount":15
  },{
    "name":"U2345678",
    "amount":10
  }],
  "default_method":"N"
}
requests.put(url=request_url, json=json_content
```

```
curl \
--url {{baseUrl}}/iserver/account/allocation/group \
--request PUT
--header 'Content-Type:application/json' \
--data '{
  "name":"new_test_group",
  "prev_name":"Group_1_NetLiq",
  "accounts":[{
    "name":"U1234567",
    "amount":10
  },{
    "name":"U2345678",
    "amount":5
  }],
  "default_method":"A"
}'
```

#### Response Object

**success:** bool.  
 Confirms that the allocation group was properly set.

```
{
  "success": true
}
```
