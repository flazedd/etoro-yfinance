### Create or Modify Alert Copy Location

Endpoint used to create a new alert, or modify an existing alert.

`POST /iserver/account/{{ accountId }}/alert`

###### Path Params

**accountId:** String.  Required  
 Identifier for the unique account to retrieve information from.  
 Value Format: “DU1234567”

###### Body Prams

**alertName**: *String.* Required  
 Used as a human-readable identifier for your created alert.  
 Format Structure: “Alert Name”

**alertMessage**: *String. Required*  
 The body content of what your alert will report once triggered  
 Value Format: “MESSAGE TEXT”

**alertRepeatable**: *int. Required*  
 Boolean number (0, 1) signifies if an alert can be triggered more than once.  
 A value of ‘1’ is required for MTA alerts  
 Value Format:

**email**: *String*. Required if ‘sendMessage’ == 1  
 Email address you want to send email alerts to  
 Value Format:

**expireTime**: *String*.Required if ‘tif’ == ‘GTD’  
 Used with a tif of “GTD” only. Signifies time when the alert should terminate if no alert is triggered.  
 Value Format: “YYYYMMDD-HH:mm:ss”

**iTWSOrdersOnly**: *int.* Optional  
 Boolean number (0, 1) to allow alerts to trigger alerts through the mobile app.  
 Value Format: 1

**outsideRth**: *int. Required*  
 Boolean number (0, 1) to allow the alert to trigger outside of regular trading hours.  
 Value Format: 1

**sendMessage**: *int. Optional*  
 Boolean number (0, 1) to allow alerts to trigger email messages  
 Value Format: 1

**showPopup**: *int. Optional*  
 Boolean number (0, 1) to allow alerts to trigger TWS Pop-up messages  
 Value Format: 1

**tif**: *String.. Required*  
 Time in Force duration of alert. Allowed: [“GTC”, “GTD”]  
 Value Format: “DAY”

**conditions**: *List of Arrays**. Required*  
 Container for all conditions applied for an alert to trigger.  
 Required field.  
 Value Format:[ {…} ]

**conidex**: *String. Required*  
 Concatenation of conid and exchange. Formatted as “conid@exchange”  
 Value Format: “265598@SMART”

**logicBind**: *String. Required*  
 Describes how multiple conditions should behave together.  
 Allowed values are: {“a”: “AND”, “o”: “OR”, “n”: “END”}  
 Value Format: “a”

**operator**: *String. Required*  
 Indicates whether the trigger should be above or below the given value.  
 Value Format:”>=”

**timeZone**: *String. Required for MTA alerts*  
 Only needed for some MTA alert condition  
 Value Format: “US/Eastern”

**triggerMethod**: *String. Required*  
 Pass the string representation of zero, “0”  
 Value Format: “0”

**type**: *int. Required*  
 Designate what condition type to use.  
 Allowed values: {1: Price, 3: Time, 4: Margin, 5: Trade, 6: Volume, 7: MTA market, 8: MTA Position, 9: MTA Account Daily PnL}  
 Value Format: 1

**value**: *String. Required*  
 Trigger value based on Type. Allows a default value of “\*”.  
 Value Format: “195.00”, “YYYYMMDD-HH:mm:ss”

}

]

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/U1234567/alert"
json_content = {
  "alertMessage": "AAPL Price Drop!",
  "alertName": "AAPL_Price",
  "expireTime":"20270101-12:00:00",
  "alertRepeatable": 0,
  "outsideRth": 0,
  "sendMessage": 1,
  "email": "user@domain.net",
  "iTWSOrdersOnly": 0,
  "showPopup": 0,
  "tif": "GTD",
  "conditions": [{
    "conidex": "265598@SMART",
    "logicBind": "n",
    "operator": "<=",
    "triggerMethod": 0,
    "type": 1,
    "value": "183.34"
  }]
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account/U1234567/alert \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "alertMessage": "AAPL Price Drop!",
  "alertName": "AAPL_Price",
  "expireTime":"20231231-12:00:00",
  "alertRepeatable": 0,
  "outsideRth": 0,
  "sendMessage": 0,
  "email": "user@domain.net",
  "iTWSOrdersOnly": 0,
  "showPopup": 0,
  "tif": "GTD",
  "conditions": [{
    "conidex": "265598@SMART",
    "logicBind": "n",
    "operator": "<=,
    "triggerMethod": 0,
    "type": 1,
    "value": "183.34"
  }]
}'
```

#### Response Object:

Returns a single json object

**request\_id: integer.** Always returns ‘null’

**order\_id: integer.** Signifies tracking ID for given alert.

**success: boolean.** Displays result status of alert request

**text: String.** Response message to clarify success status reason.

**order\_status: String.** Returns ‘null’

**warning\_message: String.** Returns ‘null’  
 }

```
{
  "request_id": null,
  "order_id": 9876543210,
  "success": true,
  "text": "Submitted",
  "order_status": null,
  "warning_message": null
}
```
