### Live Market Data Snapshot Copy Location

Get Market Data for the given conid(s).

A pre-flight request must be made prior to ever receiving data. For some fields, it may take more than a few moments to receive information.

See response fields for a list of available fields that can be request via fields argument.

The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot.

For derivative contracts the endpoint /iserver/secdef/search must be called first.

```
GET /iserver/marketdata/snapshot
```

#### Request Object

###### Query Parameters

**conids:** String. Required  
 Contract identifier for the contract of interest. A maximum of 100 conids may be specified.  
 May provide a comma-separated series of contract identifiers.

**fields:** String. Required  
 Specify a series of tick values to be returned. A maximum of 50 fields may be specified.  
 May provide a comma-separated series of field ids.  
 See [Market Data Fields](#market-data-fields) for more information.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/marketdata/snapshot?conids=265598,8314&fields=31,84,86"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/marketdata/snapshot?conids=265598,8314&fields=31,84,86 \ 
--request GET
```

#### Response Object

**server\_id:** String.  
 Returns the request’s identifier.

**conidEx:** String.  
 Returns the passed conid field. May include exchange if specified in request.

**conid:** int.  
 Returns the contract id of the request

**\_updated:** int\*.  
 Returns the epoch time of the update in a 13 character integer .

**6119:** String.  
 Field value of the server\_id. Returns the request’s identifier.

**fields\*:** String.  
 Returns a response for each request. Some fields not be as readily available as others. See the Market Data section for more details.

**6509:** String.  
 Returns a multi-character value representing the [Market Data Availability.](#md-availability)

```
[
  {
    "_updated": 1702334859712,
    "conidEx": "265598",
    "conid": 265598,
    "server_id": "q1",
    "6119": "serverId",
    "31": "193.18",
    "84": "193.06",
    "86":"193.14", 
    "6509": "RpB"
  }
]
```
