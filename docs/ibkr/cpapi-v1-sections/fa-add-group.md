### Add Allocation Group Copy Location

Add a new allocation group. This group can be used to trade

`POST /iserver/account/allocation/group`

#### Request Object

###### Body Params

**name:** String. Required Required  
 Name used to refer to your allocation group. This will be used while placing orders.

**accounts:** Array of objects. Required  
 Contains a series of objects depicting which accounts are involved and, for user-defined allocation methods, the distribution value for each sub-account.  
 [{  
 **name:** String. Required  
 The accountId of a given sub-account.  
 Value Format: “U1234567”

**amount:** Number.  
 The total distribution value for each sub-account for user-defined allocation methods.  
 }]  
 **default\_method:** String.  
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
    "amount":10
  },{
    "name":"U2345678",
    "amount":5
  }],
  "default_method":"N"
}
requests.post(url=request_url, json=json_content
```

```
curl \
--url {{baseUrl}}/iserver/account/allocation/group \
--request POST
--header 'Content-Type:application/json' \
--data '{
  "name":"Group_1_NetLiq",
  "accounts":[{
    "name":"U1234567",
    "amount":10
  },{
    "name":"U2345678",
    "amount":5
  }],
  "default_method":"N"
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
