### Endpoint Copy Location

The Access Token endpoint will be used to return the Access Token and Access Token Secret values to be used for all requests moving forward as an identifier of the user with our consumer key.

An Access Token will remain the same whenever a username is generated with a given consumer key; however, the access token secret will be unique upon each generation.

`POST /oauth/access_token`
