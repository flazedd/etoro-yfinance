### HMDS Market Scanner Copy Location

Request a market scanner from our HMDS service.

Can return a maximum of 250 contracts.

Developers should first call the [/hmds/auth/init](/campus/ibkr-api-page/cpapi-v1/#hmds-init) endpoint prior to their request to avoid an initial 404 rejection.

`POST /hmds/scanner`

#### Request Object

###### Body Parameters

**instrument:** String. Required  
 Specify the type of instrument for the request.  
 Found under the “instrument\_list” value of the /iserver/scanner/params request.

**locations:** String. Required  
 Specify the type of location for the request.  
 Found under the “location\_tree” value of the /iserver/scanner/params request.

**scanCode:** String. Required  
 Specify the scanner type for the request.  
 Found under the “scan\_type\_list” value of the /iserver/scanner/params request.

**secType:** String. Required  
 Specify the type of security type for the request.  
 Found under the “location\_tree” value of the /iserver/scanner/params request.

**delayedLocations:** null.  
 Internal use only.

**maxItems:** int.  
 Specify how many items should be returned.  
 Default and maximum set to 250.

**filters:** Array of object. Required\*  
 Array of objects containing all filters upon the scanner request.  
 Content contains a series of key:value pairs.  
 While “filters” must be specified in the body, no content in the array needs to be passed.

- Python
- cURL

```
request_url = f"{baseUrl}/hmds/scanner"
json_content= {
  "instrument":"BOND",
  "locations": "BOND.US",
  "scanCode": "HIGH_BOND_ASK_YIELD_ALL",
  "secType": "BOND",
  "delayedLocations":"SMART",
  "maxItems":25,
  "filters":[{
    "bondAskYieldBelow": 15.819
  }]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/hmds/scanner \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "instrument":"BOND",
  "locations": "BOND.US",
  "scanCode": "HIGH_BOND_ASK_YIELD_ALL",
  "secType": "BOND",
  "delayedLocations":"SMART",
  "maxItems":25,
  "filters":[{
    "bondAskYieldBelow": 15.819
  }]
}'
```

#### Response Object

**contracts:** Array of objects.  
 Contains all contracts in order from the scanner response.  
 [{  
 **inScanTime:** String.  
 Returns the time at which the contract was scanned.  
 Always returned in UTC time as a string.

**contractID:** String.  
 Returns the contract identifier of the scanned contract.

**con\_id:** String.  
 Returns the contract identifier of the scanned contract.  
 }]

```
{
  "total": "17262",
  "size": "250",
  "offset": "0",
  "scanTime": "20231214-18:55:25",
  "id": "scanner1",
  "position": "v1:AAAAAQABG3gAAAAAAAAA+g==",
  "Contracts": {
    "Contract": [
      {
        "inScanTime": "20231214-18:55:25",
        "contractID": "431424315"
      },
  ]
}
```
