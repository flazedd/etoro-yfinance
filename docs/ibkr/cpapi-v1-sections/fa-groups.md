### List All Allocation Groups Copy Location

Retrieves a list of all of the advisor’s allocation groups. This describes the name of the allocation group, number of subaccounts within the group, and the method in use for the group.

`GET /iserver/account/allocation/group`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/allocation/group" 
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/account/allocation/group \
--request GET
```

#### Response Object

**data:** Array of objects.  
 Contains object pairs for each allocation groups  
 [{  
 **allocation\_method:** String.  
 Uses the Allocation Method Code to represent which method is implemented.

**size:** int.  
 Represents the total number of sub-accounts within the group.

**name:** String.  
 The name set for the given allocation group.  
 }]

```
{
  "data": [
    {
      "allocation_method": "N",
      "size": 10,
      "name": "Group_1_NetLiq"
    }
  ]
}
```
