### Iserver Scanner Parameters Copy Location

Returns an xml file containing all available parameters to be sent for the Iserver scanner request.

```
GET /iserver/scanner/params
```

#### Request Object

No parameters or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/scanner/params"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/scanner/params \
--request GET
```

#### Response Object

**scan\_type\_list:** List Array of objects.  
 Contains all values used as the scanner “type” in the request.  
 [{  
 **display\_name:** String.  
 Human readable name for the scanner “type”

**code:** String.  
 Value used for the market scanner request.

**instruments:** Array of Strings.  
 Returns all instruments the scanner type can be used with.  
 }]

**instrument\_list:** Array of Objects.  
 Contains all values relevant to the scanner “instrument” request field.  
 [{  
 **display\_name:** String.  
 Human readable representation of the instrument type.

**type:** String.  
 Value used for the market scanner request.

**filters:** Array of Strings.  
 Returns an array of all filters uniquely avaliable to that instrument type.  
 }]

**filter\_list:** Array of Objects.  
 [{  
 **group:** String.  
 Returns the group of filters the request is affiliated with.

**display\_name:** String.  
 Returns the human-readable identifier for the filter.

**code:** String.  
 Value used for the market scanner request.

**type:** String.  
 Returns the type of value to be used in the request.  
 This can indicate a range based value, or if it should be a single value.  
 }]

**location\_tree:** Array of objects.  
 Contains all values relevant to the location field of the market scanner request.

**display\_name:** String.  
 Returns the overarching instrument type to designate the location.

**type:** String.  
 Returns the code value of the market scanner instrument type value.

**locations:** Array of objects.  
 [{  
 **display\_name:** String.  
 Returns the human-readable value of the market scanner’s location value.

**type:** String.  
 Returns the code value of the market scanner location value.

**locations:** Array.  
 Always returns an empty array at this depth.  
 }]

]

```
{
  "scan_type_list":[
    {
      "display_name": "display_name",
      "code": "code",
      "instruments": []
    }
  ],
  "instrument_list":[ 
    {
      "display_name": "display_name",
      "type": "type",
      "filters": []
    }
  ],
  "filter_list":[
    {
      "group": "group",
      "display_name": "display_name",
      "code": "code",
      "type": "type"
    }
  ],
  "location_tree":[
    {
      "display_name": "display_name",
      "type": "type",
      "locations": [
        {
          "display_name": "display_name",
          "type": "type",
          "locations": []
        }
      ]
    }
  ]
}
```
