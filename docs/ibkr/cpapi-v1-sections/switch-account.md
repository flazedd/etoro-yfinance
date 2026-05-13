### Switch Account Copy Location

Switch the active account for how you request data.

Only available for financial advisors and multi-account structures.

`POST /iserver/account`

#### Request Object:

###### Body Parameters

**acctId:** *String*. Required  
 Identifier for the unique account to retrieve information from.  
 Value Format: “DU1234567”

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account"
json_content = {
  "acctId": "U1234567,
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/account \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "acctId": "U1234567,
}'
```

#### Response Object:

**set:** bool.  
 Confirms that the account change was set.

**acctId:** String.  
 Confirms the account switched to.

```
{
    "set": true,
    "acctId": "U1234567
}
```
