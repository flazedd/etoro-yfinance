### Required Headers Copy Location

In order to make a successful request, several headers must be included. Some libraries and modules may automatically include these values, though they must always be received by Interactive Brokers in order to successfully process request.

- Accept: This must be set to “\*/\*”
- Accept-Encoding: This must be set to “gzip,deflate”
- Authorization: See our prior [Authorization Header](/campus/ibkr-api-page/cpapi-v1/#standard-auth-header) step.
- Connection: This must be set to “keep-alive”.
- Host: This must be set to “api.ibkr.com”
- User-Agent: This may be anything, though the browser identifier or request language is suggested.

- Python
- C#

```
# Add User-Agent header, required for all requests. Can have any value.
headers = {
    "Authorization":oauth_header,
    "User-Agent":"python/3.11"
}
```

```
// Build out our request headers
request.Headers.Add("Authorization", oauth_header);
request.Headers.Add("Accept", "*/*");
request.Headers.Add("Accept-Encoding", "gzip,deflate");
request.Headers.Add("Connection", "keep-alive");
request.Headers.Add("Host", "api.ibkr.com");
request.Headers.Add("User-Agent", "csharp/6.0");
```
