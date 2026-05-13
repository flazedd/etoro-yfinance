### Request Token Copy Location

For Third Party OAuth users to start the OAuth process, we must first get a request token.

To get a request token, an OAuth request to `https://api.ibkr.com/v1/api/oauth/request_token` must be made.

The request should be a POST request but with no body. Remember that [an authorization header](/campus/ibkr-api-page/cpapi-v1/#auth-header) has to be authorize the connection.

This step is a good indicator of whether or not something is wrong with your OAuth request. If you are missing any portion of the authorization header, the response will tell you so. If something is wrong with either the base string or signature creation, then you will be met with a 401 response.

**Important:** If you are a First Party OAuth users, do not follow this step. You will receive an error. For developers implementing First Party OAuth, proceed directly to [Requesting the Live Session Token](/campus/ibkr-api-page/cpapi-v1/#lst).
