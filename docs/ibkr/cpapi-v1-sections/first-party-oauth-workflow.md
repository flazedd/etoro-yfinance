### First Party OAuth Workflow Copy Location

Once you are registered in the Self-Service portal, all authentication will begin with the /live\_session\_token endpoint. Then you may begin making [Authenticated Requests With OAuth 1.0A](/campus/ibkr-api-page/cpapi-v1/#standard-oauth) for our [Standard Endpoints](/campus/ibkr-api-page/cpapi-v1/#endpoints).

[Live Session Token Endpoint](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#lst)

##### Important:

First Party OAuth registrants can not use the /request\_token, /authorize, or /access\_token endpoints. Attempts to do so will result in error.
