### Validate SSO Copy Location

Validates the current session for the SSO user.

This endpoint is only valid for Client Portal Gateway and OAuth 2.0 clients.

```
GET /sso/validate
```

#### Request Object:

No additional parameters necessary.

- Python
- cURL

```
request_url = f"{baseUrl}/sso/validate"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/sso/validate \
--request GET
```

#### Response Object:

**USER\_ID:** int.  
 Internal user identifier.

**USER\_NAME:** String.  
 current username logged in for the session.

**RESULT:** bool.  
 Confirms if validation was successful.  
 true if session was validated; false if not.

**AUTH\_TIME:** int.  
 Returns the time of authentication in epoch time.

**SF\_ENABLED:** bool.  
 Internal use only.

**IS\_FREE\_TRIAL:** bool.  
 Returns if the account is a trial account or a funded account.

**CREDENTIAL:** String.  
 Returns the underlying username of the account.

**IP:** String.  
 Internal use only.  
 Does not reflect the IP address of the user.

**EXPIRES:** int.  
 Returns the time until expiration in milliseconds.

**QUALIFIED\_FOR\_MOBILE\_AUTH:** bool.  
 Returns if the customer requires two factor authentication.

**LANDING\_APP:** String.  
 Used for Client Portal (Internal use only)

**IS\_MASTER:** bool.  
 Returns whether the account is a master account (true) or subaccount (false).

**lastAccessed:** int.  
 Returns the last time the user was accessed in epoch time.

**loginType:** int.  
 Returns the login type.  
 1 for Live, 2 for Paper

**PAPER\_USER\_NAME:** Returns the paper username for the account.

**features:** object.  
 Returns supported features such as bonds and option trading.

```
{
  "USER_ID": 123456789,
  "USER_NAME": "user1234",
  "RESULT": true,
  "AUTH_TIME": 1702580846836,
  "SF_ENABLED": false,
  "IS_FREE_TRIAL": false,
  "CREDENTIAL": "user1234",
  "IP": "12.345.678.901",
  "EXPIRES": 415890,
  "QUALIFIED_FOR_MOBILE_AUTH": null,
  "LANDING_APP": "UNIVERSAL",
  "IS_MASTER": false,
  "lastAccessed": 1702581069652,
  "LOGIN_TYPE": 2,
  "PAPER_USER_NAME": "user1234",
  "features": {
    "env": "PROD",
    "wlms": true,
    "realtime": true,
    "bond": true,
    "optionChains": true,
    "calendar": true,
    "newMf": true
  },
  "region": "NJ"
}
```
