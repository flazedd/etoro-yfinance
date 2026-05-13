### Retrieve Single Allocation Group Copy Location

Retrieves the configuration of a single account group. This describes the name of the allocation group, the specific accounts contained in the group, and the allocation method in use along with any relevant quantities.

`POST /iserver/account/allocation/group/single`

#### Request Object

###### Body Params

**name:** String. Required.  
 Name of an existing allocation group.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/allocation/group/single" 
json_content ={
  "name":"Group_1_NetLiq"
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account/allocation/group/single \
--request POST
--header 'Content-Type:application/json' \
--data '{"name":"Group_1_NetLiq"}'
```

#### Response Object

{ **name:** String. Required Required  
 Name used to refer to your allocation group. This will be used while placing orders.

**accounts:** Array of objects. Required  
 Contains a series of objects depicting which accounts are involved and, for user-defined allocation methods, the distribution value for each sub-account.  
 [  
 {  
 **name:** String. Required  
 The accountId of a given sub-account.  
 Value Format: “U1234567”

**amount:** Number.  
 The total distribution value for each sub-account for user-defined allocation methods.  
 }  
 ]  
 **default\_method:** String.  
 Specify the allocation method code for the allocation group.  
 See Allocation Method Codes for more details.  
 }

```
{
  "name": "Group_1_NetLiq",
  "accounts": [
    {
      "amount": 1,
      "name": "DU1234567"
    },
    {
      "amount": 5,
      "name": "DU9876543"
    }
  ],
  "default_method": "R"
}
```
