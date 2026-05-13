### Access Token Copy Location

A POST request to https://api.ibkr.com/v1/api/oauth/access\_token must now be made.

This time, oauth\_verifier must be added to the authorization header, with the value being the verifier token retrieved from the previous step.

oauth\_token must also be added to the authorization header, the value being [the request token](/campus/ibkr-api-page/cpapi-v1/#request-token).

If the request succeeds, the response will contain two values: oauth\_token and oauth\_token\_secret.

The oauth\_token in the response is the access token, and the oauth\_token\_secret will be used for the next step.

**Important:** If you are a First Party OAuth users, do not follow this step. You will receive an error The access token and access token secret would otherwise be retrieved through the Self Service Portal. For developers implementing First Party OAuth, proceed directly to [Requesting the Live Session Token](/campus/ibkr-api-page/cpapi-v1/#lst).
