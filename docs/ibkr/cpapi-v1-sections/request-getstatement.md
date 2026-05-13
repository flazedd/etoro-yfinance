### Make request to /GetStatement Copy Location

###### Query Params

**t**. Required  
 Accepts the **Access Token** created for the Flex Web Service in Client Portal’s Account Settings interface.

**q** Required  
 Accepts the **ReferenceCode** returned by the previous successful request, which identifies the instance of the report to be retrieved. Note that a given Flex Query template can be used to generate multiple reports over time, each populated with data at the time of generation, so this ReferenceCode identifier is used to retrieve a specific instance, presumably the one generated immediately prior.

**v**. Required, leave value = 3  
 Specifies the **version** of the Flex Web Service to be used. Values `2` and `3` are supported, but version 3 should always be used.

- Python

```
tree = ET.ElementTree(ET.fromstring(flexReq.text))
root = tree.getroot()

for child in root:
    if child.tag == "Status":
        if child.text != "Success":
            print(f"Failed to generate Flex statement. Stopping...")
            exit()
    elif child.tag == "ReferenceCode":
        refCode = child.text

print("Hold for Request.")
time.sleep(20)

receive_slug = "/GetStatement"
receive_params = {
    "t":token, 
    "q":refCode, 
    "v":flex_version
}

receiveUrl = requests.get(url=requestBase+receive_slug, params=receive_params, allow_redirects=True)

open(csvPath, 'wb').write(receiveUrl.content)
```
