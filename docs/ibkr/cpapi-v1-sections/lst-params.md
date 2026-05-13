### OAuth Params Copy Location

**oauth\_consumer\_key:** String. Required  
 The 9-character string that was obtained from Interactive Brokers during the OAuth consumer registration process. This is set in the Self Service Portal.

**oauth\_token:** String. Required  
 The access token obtained from IB via /access\_token or the Self Service Portal.

**oauth\_signature\_method:** String. Required  
 The signature method used to sign the request. Currently only ‘RSA-SHA256’ is supported.

**oauth\_signature:** String. Required  
 The signature for the request generated using the method specified in the oauth\_signature\_method parameter. See section 9 of the OAuth v1.0a specification for more details on signing requests.

**oauth\_timestamp:** String. Required  
 Timestamp expressed in seconds since 1/1/1970 00:00:00 GMT. Must be a positive integer and greater than or equal to any timestamp used in previous requests.

**oauth\_nonce:** String. Required  
 A random string uniquely generated for each request.

**diffie\_hellman\_challenge:** String. Required  
 Challenge value calculated using the Diffie-Hellman prime and generated provided during the registration process. See the “OAuth at Interactive Brokers” document for more details.

```
{
  "diffie_hellman_challenge": "5356ee6f78fc204b22e2012636d23116e4158ee84aa4451c4a8d3f595ec83434497073e25697ab23cc912799dadeef39fe243d317f193659e488535a31dbcb814600ffad3fd76b076e7f1c54cf045395c1f01d982a358f3202dd6b546271498040f4687959b7b240bc6222902d24e1bf5de42ae0a46cc60f41f62a58d428932a92e5954e7980384a9e1e0b918a35f0a838e0c4c3d0cb32db759b5cbda371e035740d9c0030b1619b61e928b8d12ca141bd3fe74ac10a835382125a57837c84b5bd1873bd118f92657b8dd45e48652093e5c0c3a5dacfb4d140e5672ddc05eb1d90bc29c433e744ae8950e96590668a9b8503e596780b14852be639ce3b5ba2c0",
  "oauth_consumer_key": "TESTCONS",
  "oauth_token": "e84c11dc149cb96ee5bb",
  "oauth_signature_method": "RSA-SHA256",
  "oauth_signature": "czbA1dRKJSBdwn5GYxAJQCmCAqfZ6dyOa%2FgmuY%2F5Lhub64cSeQUzKp8vGrF6afnXhCiIXnHsCTONK7uNbRu2V%2FE%2FziQ57BWfbAEzH98kQdWAlWqqmaxXBzbg%2Fr1AZDRP%2FYWrEggNvJaHjbkWaotcrAWpsfxVLcdc3Sl7kXmbFYN0u20MjLUD7q5yDrJT5TXw9JC2xvFimJj65WxqyICZizQUUrg35KRQKaxytQFdwqf5RS6B65gmoi7gHXZcDu2zDWGhe67bZKV8myd0isIJZBs8a5alGd33n7Y1V7pv5Ux9hFOEHEBzSaE3kn9dqw%2Fp5w%2Fl%2F0xiOQGpXWvPRVA2uA%3D%3D",
  "oauth_timestamp": "1722886871",
  "oauth_nonce": "e8181dd345bcc1a7237df79cd1b59219",
  "realm": "test_realm"
}
```
