## Endpoints Copy Location

To make calls to create or modify data to Interactive Brokers, users must use an URL endpoint through the localhost. Each call is comprised of a base URL and an endpoint.

The base url for the [Client Portal Gateway](/campus/ibkr-api-page/cpapi-v1/#cpgw) is: **https://localhost:5000/v1/api**

By default, the Client Portal Gateway is not bundled with a signed certificate. As such, customers should either look to independently have their certificate signed, or submit requests to their localhost as ‘insecure’.

OAuth 1.0a users should route requests to **https://api.ibkr.com/v1/api** instead.

- Python
- cURL

Python web requests are displayed with various external libraries that users may wish to implement. While this documentation is built around the *requests* library, there are a few additional libraries to consider:

- requests
- json
- websocket-client

To send ‘insecure’ requests in python, add “verify=False” as a request argument.

Please note that cURL requests are formatted using the cURL standard, [documented here](https://curl.se/docs/manpage.html). Some OS specific platforms may be unique, and will require some adjustment.

Our system displays the default bash structure.

- Unix and bash use \ (backslash)
- Powershell will utlize ` (backtick)
- Command Prompt uses ^ (caret)

To send ‘insecure’ requests in cURL, add “–insecure” into the request.

#### Headers

All requests should include the following Headers:

- Host: This should be set to “api.ibkr.com”
- User-Agent: This may be set to anything, though it is best to reference your environment or pull directly from the browser.
- Accept: This should be set to “\*/\*” to indicate any return format. Typically application/json is returned, though this is not always the case.
- Connection: This should be set to “keep-alive”.
- Content-Length: Sending a POST request must include Content-Length. Requests sent without Content-Length will return a 411 error.
  - Note: Most languages pass this information by default. However, some implementations, such as Java Springboot, may not include these headers in a standard request.
