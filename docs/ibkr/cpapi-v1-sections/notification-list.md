### Get a list of notifications Copy Location

Get a list of available notifications.

`GET /fyi/notifications`

#### Request Object

###### Query Params

**max:** String.  
 Specify the maximum number of notifications to receive.  
 Can request a maximum of 10 notifications.

- Python
- cURL

```
request_url = f"{baseUrl}/fyi/notifications?max=10" 
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/fyi/notifications?max=10 \ 
--request GET
```

#### Response Object

**D:** String.  
 Notification date

**ID:** String.  
 Unique way to reference the notification.

**FC:** String.  
 FYI code, we can use it to find whether the disclaimer is accepted or not in settings

**MD:** String.  
 Content of notification.

**MS:** String.  
 Title of notification.

**R:** string.  
 Return if the notification was read or not.  
 Value Format: 0: Disabled; 1: Enabled.

```
[{
  "R": 0,
  "D": "1702469440.0",
  "MS": "IBKR FYI: Option Expiration Notification",
  "MD": "One or more option contracts in your portfolio are set to expire shortly.    
 - QQQ 15DEC2023 385 P in Account(Qty): U****7890(6)   
 - QQQ 15DEC2023 387 P in Account(Qty): D****0685(-6)   
    
Please use the Option Rollover tool to roll existing contracts into contracts with an expiration, strike and price condition of your preference.",
  "ID": "2023121370119463",
  "HT": 0,
  "FC": "OE"
}]
```
