### Authentication Frequently Asked Questions Copy Location

###### Copy Location

Q:

###### How can I tell if my brokerage session is authenticated?

A:

The endpoint **iserver/auth/status** can be used to determine the current authentication status of the session. Once you have logged in using the Client Portal API Gateway, you can make a request to this endpoint to determine if your session is fully authenticated. If the session is fully authenticated, the response from this endpoint will display  `"authenticated": true` .

###### Copy Location

Q:

###### How long does a session remain authenticated?

A:

A session can remain authenticated for up to 24 hours, resetting at midnight for New York, U.S.; Zug, Switzerland; or Hong Kong time depending on your nearest connection.

Sessions will time out after approximately 6 minutes without sending new requests or maintaining the [/tickle endpoint](/campus/ibkr-api-page/cpapi-v1/#tickle) at least every 5 minutes.

Daily maintenance of IBKR’s servers could result in a disconnect earlier than the 24 hour period mentioned above. We advise disconnecting your session from your gateway and restarting it after the maintenance time to minimize any potential problems that may arise. Information on server reset times and system status updates can be found on the [System Staus](https://www.interactivebrokers.com/en/software/systemStatus.php) page.

###### Copy Location

Q:

###### How can I prevent the session from timing out?

A:

A Client Portal API brokerage session will timeout if no requests are received within a period of 5 minutes. In order to prevent the session from timing out, the endpoint **/tickle** should be called on a regular basis. It is recommended to call this endpoint approximately every minute.

If the brokerage session has timed out but the session is still connected to the IBKR backend, the response to **/auth/status** returns ‘connected’:true and ‘authenticated’:false. Calling the [/iserver/auth/ssodh/init](/campus/ibkr-api-page/cpapi-v1/#ssodh-init) endpoint will initialize a new brokerage session.

###### Copy Location

Q:

###### Is it possible to authenticate a live brokerage session without the use of a Two Factor Authentication (2FA) device?

A:

The login process to the Client Portal API Gateway is the same as to Client Portal. As the Client Portal has access to sensitive information and banking functionalities, two-factor authentication is mandatory for login.
