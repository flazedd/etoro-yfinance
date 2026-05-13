### Create a Watchlist Copy Location

Create a watchlist to monitor a series of contracts.

`POST /iserver/watchlist`

#### Request Object

###### Body Params

**id:** String. Required  
 Supply a unique identifier to track a given watchlist. Must supply a number.

**name:** String. Required  
 Supply the human readable name of a given watchlist. Displayed in TWS and Client Portal.

**rows:** Array of Objects. Required  
 [{  
 **C:** int.  
 Provide the conid, or contract identifier, of the conid to add.

**H:** Empty String.  
 Can be used to add a blank row between contracts in the watchlist.  
 }]

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/watchlist"
json_content = {
  "id":"1234",
  "name":"Test Watchlist",
  "rows":[
    {"C":8314},
    {"C":8894}
  ]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/watchlist \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "id":"1234",
  "name":"Test Watchlist",
  "rows":[
    {"C":8314},
    {"C":8894}
  ]
}'
```

#### Response Object

**id:** String.  
 Returns the id value used to create the watchlist.

**hash:** String.  
 Returns the internal IB hash value of the order.

**name:** String.  
 Returns the human-readable name of the watchlist.

**readOnly:** bool.  
 Determines if the watchlist is marked as write-restricted.

**instruments:** Empty Array.  
 Always returns an empty array.  
 Conids supplied will still be in the final watchlist.  
 See the [/iserver/watchlist?id](/campus/ibkr-api-page/cpapi-v1/#watchlist-info) endpoint for more details.

```
{
  "id": "1234",
  "hash": "1702581306241",
  "name": "Test Watchlist",
  "readOnly": false,
  "instruments": []
}
```
