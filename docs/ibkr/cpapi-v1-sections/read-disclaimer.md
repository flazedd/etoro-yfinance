### Mark Disclaimer Read Copy Location

Mark disclaimer message read.

`PUT /fyi/disclaimer/{typecode}`

#### Request Object

###### Path Params

**typecode:** String. Required  
 Code used to signify a specific type of FYI template.  
 See [Typecode](/campus/ibkr-api-page/cpapi-v1/#fyi-typecode) section for more details.

- Python
- cURL

```
request_url = f"{baseUrl}/fyi/disclaimer/CT"
json_content = {}
requests.put(url=request_url, json=json_content
```

```
curl \
--url {{baseUrl}}/fyi/disclaimer/CT \
--request PUT \
--data ''
```

#### Response Object

**V:** int.  
 Returns 1 to state message was acknowledged.

**T:** int.  
 Returns the time in ms to complete the edit.

```
{
  "V": 1,
  "T": 10
}
```
