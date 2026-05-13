### Initial OAuth Params Copy Location

The OAuth params of standard requests are slightly different than the live session token.

**oauth\_consumer\_key:** String. Required  
 A 9-character string set during your OAuth registration process.

- Third Party OAuth: This will be provided by Interactive Brokers during the registration process.
- First Party OAuth: This is saved in the Self Service Portal.

**oauth\_nonce:** String. Required  
 A random string uniquely generated for each request.

**oauth\_timestamp:** String. Required  
 Timestamp expressed in seconds since 1/1/1970 00:00:00 GMT. Must be a positive integer and greater than or equal to any timestamp used in previous requests.

**oauth\_token:** String. Required

- Third Party OAuth: This is received from the [Access Token endpoint](/campus/ibkr-api-page/cpapi-v1/#access-token)
- First Party OAuth: This is generated in the Self Service Portal.

**oauth\_signature\_method:** String. Required  
 The signature method used to sign the request. Only ‘HMAC-SHA256’ is supported.

- Python
- C#

```
oauth_params = {
    "oauth_consumer_key": consumer_key,
    "oauth_nonce": hex(random.getrandbits(128))[2:],
    "oauth_signature_method": "HMAC-SHA256",
    "oauth_timestamp": str(int(datetime.now().timestamp())),
    "oauth_token": access_token
}
```

```
// Interactive Brokers requires a 10 digit Unix timestamp value.
// Values beyond 10 digits will result in an error.
string timestamp = DateTimeOffset.Now.ToUnixTimeMilliseconds().ToString();
timestamp = timestamp.Substring(0, timestamp.Length - 3);

// Create a Random object, and then retrieve any random positive integer value.
Random random = new();

String oauth_nonce = random.Next(1, int.MaxValue).ToString("X").ToLower();

//Create a dictionary for all oauth params in our header.
Dictionary<string, string> oauth_params = new()
{
    { "oauth_consumer_key", consumer_key },
    { "oauth_nonce", oauth_nonce },
    { "oauth_timestamp", timestamp },
    { "oauth_token", access_token },
    { "oauth_signature_method", "HMAC-SHA256" }
};
```
