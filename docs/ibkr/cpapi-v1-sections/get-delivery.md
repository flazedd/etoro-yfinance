### Get Delivery Options Copy Location

Options for sending fyis to email and other devices

`GET /fyi/deliveryoptions`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/fyi/deliveryoptions"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/fyi/deliveryoptions \
--request GET
```

#### Response Object

**M:** int.  
 Email option is enabled or not.  
 Value Format: 0: Email Disabled; 1: Email Enabled.

**E:** Array.  
 Returns an array of device information.  
 [{  
 **NM:** String.  
 Returns the human readable device name.

**I:** String.  
 Returns the deice identifier.

**UI:** String.  
 Returns the unique device ID.

**A:** String.  
 Device is enabled or not.  
 Value Format: 0: Disabled; 1: Enabled.  
 }]

```
{
  "E": [
    {
      "NM": "iPhone",
      "I": "apn://mtws@1234E5E67D8A9012EC3E45D6E7D89A01F2345CDBBB678B9BE0FB12345AF6D789",
      "UI": "apn://mtws@1234E5E67D8A9012EC3E45D6E7D89A01F2345CDBBB678B9BE0FB12345AF6D789",
      "A": 1
    }
  ],
  "M": 1
}
```
