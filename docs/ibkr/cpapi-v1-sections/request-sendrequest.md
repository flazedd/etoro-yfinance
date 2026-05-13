### Make request to /SendRequest Copy Location

**IMPORTANT:** The /SendRequest endpoint maintains a pacing limitation of 1 request per second. A maximum of 10 requests per minute may be submitted.

###### Query Params

**t**. Required  
 Accepts the **Current Token** created for the Flex Web Service in Client Portal’s Account Settings interface.

**q**. Required  
 The **Query ID** identifier for the desired report template, obtained from the Client Portal’s Flex Query interface.

**v**. Required, leave value = 3  
 Specifies the **version** of the Flex Web Service to be used. Values `2` and `3` are supported, but version 3 should always be used.

- Python

```
requestBase = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService"
token = 528191644107458877539776
queryId = 800969
flex_version = 3

send_path = "/SendRequest"
send_params = {
    "t":token, 
    "q":queryId, 
    "v":flex_version
}

flexReq = requests.get(url=requestBase+send_slug, params=send_params)
```
