### Search Algo Params by Contract ID Copy Location

Returns supported IB Algos for contract.

A pre-flight request must be submitted before retrieving information

`GET /iserver/contract/{{ conid }}/algos`

#### Request Object

###### Path Parameters

**conid:** String. Required  
 Contract identifier for the requested contract of interest.

###### Query Parameters

**algos:** String. Optional  
 List of algo ids delimited by “;” to filter by.  
 Max of 8 algos ids can be specified.  
 Case sensitive to algo id.

**addDescription:** String. Optional  
 Whether or not to add algo descriptions to response. Set to 1 for yes, 0 for no.

**addParams:** String. Optional  
 Whether or not to show algo parameters. Set to 1 for yes, 0 for no.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/contract/265598/algos?algos=Adaptive;Vwap&addDescription=1&addParams=1"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/contract/265598/algos?algos=Adaptive;Vwap&addDescription=1&addParams=1 \
--request GET
```

#### Response Object

**algos:** Array of objects.  
 Contains all relevant algos for the contract.

[{

**name:** String.  
 Common name of the algo.

**id:** String.  
 Algo identifier used for requests

**parameters:** Array of objects.  
 All parameters relevant to the given algo.  
 Only returned if addParams=1

[{

**guiRank:** int.  
 Positional ranking for the algo. Used for Client Portal.

**defaultValue:** int.  
 Default parameter value.

**name:** String.  
 Parameter name.

**id:** String.  
 Parameter identifier for the algo.

**legalStrings:** Array  
 Allowed values for the parameter.

**required:** String.  
 States whether the parameter is required for the given algo order to place.  
 Returns a string representation of a boolean.

**valueClassName:** String.  
 Returns the variable type of the parameter.  
 }]  
 }]

```
{
  "algos": [
    {
      "name": "Adaptive",
      "id": "Adaptive",
      "parameters": [
        {
          "guiRank": 1,
          "defaultValue": "Normal",
          "name": "Adaptive order priority/urgency",
          "id": "adaptivePriority",
          "legalStrings": [
            "Urgent",
            "Normal",
            "Patient"
          ],
          "required": "true",
          "valueClassName": "String"
        }
      ]
    },
    {
      "name": "VWAP",
      "id": "Vwap",
      "parameters": [
        {
          "guiRank": 5,
          "defaultValue": false,
          "name": "Attempt to never take liquidity",
          "id": "noTakeLiq",
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 11,
          "defaultValue": false,
          "name": "Opt-out closing auction",
          "id": "optoutClosingAuction",
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 4,
          "defaultValue": false,
          "name": "Allow trading past end time",
          "id": "allowPastEndTime",
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 8,
          "defaultValue": false,
          "name": "Speed up when market approaches limit price",
          "description": "Compensate for decreased fill rate due to presence of limit price.",
          "id": "speedUp",
          "enabledConditions": [
            "MKT:speedUp:=:no"
          ],
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 12,
          "name": "Trade when price is more aggressive than:",
          "description": "Evaluates with bid for buy order and ask for sell order",
          "id": "conditionalPrice",
          "valueClassName": "Double"
        },
        {
          "guiRank": 2,
          "name": "Start Time",
          "description": "Defaults to start of market trading",
          "id": "startTime",
          "valueClassName": "Time"
        },
        {
          "guiRank": 1,
          "minValue": 0.01,
          "maxValue": 50,
          "name": "Max Percentage",
          "description": "From 0.01 to 50.0",
          "id": "maxPctVol",
          "valueClassName": "Double"
        },
        {
          "guiRank": 3,
          "name": "End Time",
          "description": "Defaults to end of market trading",
          "id": "endTime",
          "valueClassName": "Time"
        }
      ]
    }
  ]
}
```
