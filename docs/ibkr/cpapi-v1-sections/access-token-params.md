### OAuth Params Copy Location

**oauth\_consumer\_key:** String. Required  
 The 25-character hexadecimal string that was obtained from Interactive Brokers during the OAuth consumer registration process.

**oauth\_token:** String. Required  
 The request token obtained from IB via /request\_token.

**oauth\_signature\_method:** String. Required  
 The signature method used to sign the request. Currently only ‘RSA-SHA256’ is supported.

**oauth\_signature:** String. Required  
 The signature for the request.

**oauth\_timestamp:** String. Required  
 Timestamp expressed in seconds since 1/1/1970 00:00:00 GMT. Must be a positive integer and greater than or equal to any timestamp used in previous requests.

**oauth\_nonce:** String. Required  
 A random string uniquely generated for each request.

**oauth\_verifier:** String. Required  
 The verification code received from IB after the user has granted authorization.

```
{
  "oauth_consumer_key": "TESTCONS",
  "oauth_token": "47b63b7961c51e1df1e6",
  "oauth_signature_method": "RSA-SHA256",
  "oauth_signature": "V9p9e41Zx8Fsi1QkJq3QewZdt%2BZM8GTCcKswY08MbZKCHsob57JEdNbpeANWkiwqVdDnRArQ52ifQsutYlvXvsUQAVd2vuiMqcEqpGN8c2ZmTqVQbQwNaqw0LLXQ84DmwDUWJa%2F8pSJPmCmMPi4tJPKb%2Bta1DyVN2ec8KwzRw8c7MpKsbKBXXC%2B0vJ7Y8kTE0WnoiPA%2FJ8sRn7sZnlsDlEmyxNY%2Fggrr%2F5GJTQFe2EXka5eMsHrnWTYdC1tg38%2BVebt4HNyptLUCO0%2FpeZVRbjN3RyfPlDpSlJ6jGh2lqtcyLEueDsxvN%2FsRWjpiBl1in%2Bou6YYeB2D%2FBz%2Bttvpagw%3D%3D",
  "oauth_timestamp": "1722030398",
  "oauth_nonce": "734860ccbc2f14ae971a8cf1a6ec936",
  "oauth_verifier": "01028463e73960e27b3f"
}
```
