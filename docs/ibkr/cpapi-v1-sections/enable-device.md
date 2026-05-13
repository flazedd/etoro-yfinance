### Enable/Disable Device Option Copy Location

Choose whether a particular device is enabled or disabled.

`POST /fyi/deliveryoptions/device`

#### Request Object

###### Body Params

**devicename:** String. Required  
 Human readable name of the device.

**deviceId:** String. Required  
 ID Code for the specific device.

**uiName:** String. Required  
 Title used for the interface system.

**enabled:** bool. Required  
 Specify if the device should be enabled or disabled.

- Python
- cURL

```
request_url = f"{baseUrl}/fyi/deliveryoptions/device"
json_content = {
    "deviceName": "iPhone",
    "deviceId": "apn://mtws@1234E5E67D8A9012EC3E45D6E7D89A01F2345CDBBB678B9BE0FB12345AF6D789",
    "uiName": "apn://mtws@1234E5E67D8A9012EC3E45D6E7D89A01F2345CDBBB678B9BE0FB12345AF6D789",
    "enabled": True
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/fyi/deliveryoptions/device \
--request POST \
--data '{
    "deviceName": "iPhone",
    "deviceId": "apn://mtws@1234E5E67D8A9012EC3E45D6E7D89A01F2345CDBBB678B9BE0FB12345AF6D789",
    "uiName": "apn://mtws@1234E5E67D8A9012EC3E45D6E7D89A01F2345CDBBB678B9BE0FB12345AF6D789",
    "enabled": True
}'
```

#### Response Object

**V:** int.  
 Returns 1 to state message was acknowledged.

**T:** int.  
 Returns the time in ms to complete the edit.

```
{
  "V": 1,
  "T": 10
}
```
