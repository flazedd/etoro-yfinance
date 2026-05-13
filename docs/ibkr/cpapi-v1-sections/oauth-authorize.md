### Authorization Copy Location

After retrieving our request token, we need to authorize the value against the Interactive Brokers server. This is done by directing users to https://interactivebrokers.com/authorize?oauth\_token={{ REQUEST\_TOKEN }} where they will log in with their Interactive Brokers credentials. Because we are using “oob” as our callback url, users will be presented with an error page.

Replace REQUEST\_TOKEN with the request token you generated

After the user logs in, they will be redirected to a URL specified during consumer key creation, and there will be two query parameters in the URL:  
 oauth\_token and oauth\_verifier

oauth\_token is the request token, and oauth\_verifier is the verifier token required for the next step.

An example of url after the user logs in `https://localhost:20000/?oauth_token=b9082d68cfef06b030de&oauth_verifier=0ffb93ab9aa0d2177cc2`

**Important:** If you are a First Party OAuth users, do not follow this step. You will receive an error. For developers implementing First Party OAuth, proceed directly to [Requesting the Live Session Token](/campus/ibkr-api-page/cpapi-v1/#lst).
