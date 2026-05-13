### OAuth Parameters Copy Location

**oauth\_consumer\_key:** String. Required  
 The 25-character hexadecimal string that was obtained from Interactive Brokers during the OAuth consumer registration process.

**oauth\_signature\_method:** String. Required  
 The signature method used to sign the request. Currently only ‘RSA-SHA256’ is supported.

**oauth\_signature:** String. Required  
 The signature for the request generated using the method specified in the oauth\_signature\_method parameter. See section 9 of the OAuth v1.0a specification for more details on signing requests.

**oauth\_timestamp:** String. Required  
 Timestamp expressed in seconds since 1/1/1970 00:00:00 GMT. Must be a positive integer and greater than or equal to any timestamp used in previous requests.

**oauth\_nonce:** String. Required  
 A random string uniquely generated for each request.

**oauth\_callback:** String. Required  
 An absolute URL to which IB will redirect the user. This URL would be provided to the onboarding team during initial integration, or ‘oob’ can be provided for localhost development.

```
{
  "oauth_consumer_key": "TESTCONS",
  "oauth_signature_method": "RSA-SHA256",
  "oauth_signature": "fnHGXncCkcnB3U3jYxjh%2BgUdo7PelK5NQGIedbDeAQgDtO02ccLVapH5QtpazS%2BKlwg7bJTAgxsM1T5QOox6IjBQJu91EJ%2FFVUCFtd8rNbRQNGbEWdibglWErBDuHY%2FVCLRHdCqAg9BhV%2BZ7FTY6oCT9HSQr6ZK%2FgNqTd58vpt5z8cPCoPHRJN4HzB54J5A4K7R7aEx9s1B5wqIer7fdVIzKb0KSSpP44Hx%2BGnLfZINfQHIrRCfFwbeGEvi31PF9ICWRIKZz5LxqX6OtT0Dze8LiZo7PnkrA5b0m9PR0cP1v6DSBVaSyJXBITiml9Gyn2HuiexHjRJt85gPhNiU3VA%3D%3D",
  "oauth_timestamp": "1722886851",
  "oauth_nonce": "a568f4e3b0e161b0dcf187331b8274be",
  "oauth_callback": "oob"
}
```
