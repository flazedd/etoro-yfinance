### Iserver Market Scanner Copy Location

Searches for contracts according to the filters specified in /iserver/scanner/params endpoint

Users can receive a maximum of 50 contracts from 1 request.

`POST /iserver/scanner/run`

#### Request Object

###### Body Parameters

**instrument:** String. Required  
 Instrument type as the target of the market scanner request.  
 Found in the “instrument\_list” section of the /iserver/scanner/params response.

**type:** String. Required  
 Scanner value the market scanner is sorted by.  
 Based on the “scan\_type\_list” section of the /iserver/scanner/params response.

**location:** String. Required  
 Location value the market scanner is searching through.  
 Based on the “location\_tree” section of the /iserver/scanner/params response.

**filter:** Array of objects.  
 Contains any additional filters that should apply to response.  
 [{  
 **code:** String.  
 Code value of the filter.  
 Based on the “code” value within the “filter\_list” section of the /iserver/scanner/params response.

**value:** int.  
 Value corresponding to the input for “code”.  
 }]

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/scanner/run"
json_content = {
  "instrument": "STK",
  "location": "STK.US.MAJOR",
  "type": "TOP_TRADE_COUNT",
  "filter": [
    {
      "code":"priceAbove",
      "value":5
    }
  ]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl/iserver/scanner/run \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "instrument": "STK",
  "location": "STK.US.MAJOR",
  "type": "TOP_PERC_GAIN",
  "filter": [
    {
      "code":"priceAbove",
      "value":5
    }
  ]
}'
```

#### Response Object

**contracts:** Array of objects.  
 Contains contracts related to the market scanner request.  
 [{  
 **server\_id:** String.  
 Contract’s index in relation to the market scanner type’s sorting priority.

**column\_name:** String.  
 Always returned for the first contract.  
 Used for Client Portal (Internal use only)

**symbol:** String.  
 Returns the contract’s ticker symbol.

**conidex:** String.  
 Returns the contract ID of the contract.

**con\_id:** int.  
 Returns the contract ID of the contract.

**available\_chart\_periods:** String.  
 Used for Client Portal (Internal use only)

**company\_name:** String.  
 Returns the company long name.

**contract\_description\_1:** String.  
 For derivatives like Futures, the local symbol of the contract will be returned.

**listing\_exchange:** String.  
 Returns the primary listing exchange of the contract.

**sec\_type:** String.  
 Returns the security type of the contract.  
 }],

**scan\_data\_column\_name:** String.  
 Used for Client Portal (Internal use only)

```
{
  "contracts": [
    {
      "server_id": "0",
      "symbol": "AMD",
      "conidex": "4391",
      "con_id": 4391,
      "available_chart_periods": "#R|1",
      "company_name": "ADVANCED MICRO DEVICES",
      "scan_data": "163.773K",
      "contract_description_1": "AMD",
      "listing_exchange": "NASDAQ.NMS",
      "sec_type": "STK"
    }
  ],
  "scan_data_column_name": "Trades"
}
```
