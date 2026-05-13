### Delete a Device Copy Location

Delete a specific device from our saved list of notification devices.

`DELETE /fyi/deliveryoptions/{{ deviceId }}`

#### Request Object

###### Path Params

**deviceId:** String. Required  
 Display the device identifier to delete from IB’s saved list.  
 Can be retrieved from [/fyi/deliveryoptions](/campus/ibkr-api-page/cpapi-v1/#get-delivery).

- Python
- cURL

```
request_url = f"{baseUrl}/fyi/deliveryoptions/1" 
requests.delete(url=request_url)
```

```
curl \
--url {{baseUrl}}/fyi/deliveryoptions/1 \ 
--request DELETE
```

#### Response Object

No response message is returned. Instead, you will only receive an empty string with a 200 OK status code indicating a successfully deleted account.
