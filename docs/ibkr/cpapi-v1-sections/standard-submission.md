### Submit The Request Copy Location

After calculating our Authorization header creating our headers, we can submit the request. As mentioned in our [Endpoints section](/campus/ibkr-api-page/cpapi-v1/#endpoints), all content would then be submitted as JSON formatting. Examples in the respective languages have been included for our example.

- Python
- C#

```
json_data = {"publish":True, "compete":True}

# end request to /ssodh/init, print request and response.
init_request = requests.post(url=url, headers=headers, json=json_data)
if init_request.status_code == 200:
    print(init_request.content)
```

```
string req_content = JsonSerializer.Serialize(new { compete = true, publish = true });
StringContent req_content_json = new(req_content, Encoding.UTF8, "application/json");
request.Content = req_content_json;
HttpResponseMessage response = client.SendAsync(request).Result;
```
