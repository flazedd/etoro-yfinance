### Set Dynamic Account Copy Location

Broker accounts configured with the DYNACCT property will not receive account information at login. Instead, they must dynamically query then set their account number.

##### Important:

This will not function for individual or financial advisor accounts. This will only be functional for IBrokers with the DYNACCT property approved.

Customers without the DYNACCT property will receive the following message

```
{
    "error": "Details currently unavailable. Please try again later and contact client services if the issue persists.",
    "statusCode": 503
}
```

Set the active dynamic account. Values retrieved from [Search Dynamic Account](/campus/ibkr-api-page/cpapi-v1/#get-dynamic-account)

`POST /iserver/dynaccount`

#### Request Object

###### Body Params

**acctId:** String. Required  
 The account ID that should be set for future requests.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/dynaccount"
json_content = {
  "acctId": "U1234567
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/dynaccount \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "acctId": "U1234567
}'
```

#### Response Object

**set:** bool.  
 Confirms if the account change was fully set.

**acctId:** String.  
 The account ID that was set for future use.

```
{
  "set": "true",
  "acctId": "U1234567",
}
```
