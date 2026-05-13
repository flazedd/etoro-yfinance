### OAuth Signature Copy Location

Creating the OAuth Signature is a multi-stage process.

1. First uses will need to create an HMAC Sha256 hash of the encoded base string
   1. You must use a Base64 byte array of our live session token as the Key value.
2. Then, hash the encoded byte string using our new HMAC Sha256 object.
3. Convert the resulting bytes into a Base64 encoded string.
4. Then URI escape our string, again using [Rfc3986](https://datatracker.ietf.org/doc/html/rfc3986), to receive our final oauth\_signature value.

- Python
- C#

```
# Generate bytestring HMAC hash of base string bytestring.
# Hash key is base64-decoded LST bytestring, method is SHA256.
bytes_hmac_hash = HMAC.new(
    key=base64.b64decode(live_session_token), 
    msg=base_string.encode("utf-8"),
    digestmod=SHA256
    ).digest()

# Generate str from base64-encoded bytestring hash.
b64_str_hmac_hash = base64.b64encode(bytes_hmac_hash).decode("utf-8")

# URL-encode the base64 hash str and add to oauth params dict.
oauth_params["oauth_signature"] = quote_plus(b64_str_hmac_hash)
```

```
// Create HMAC SHA256 object
HMACSHA256 bytes_hmac_hash_K = new()
{
    // Set the HMAC key to our live_session_token
    Key = Convert.FromBase64String(computed_lst)
};

// Hash the SHA256 bytes against our encoded bytes.
byte[] K_hash = bytes_hmac_hash_K.ComputeHash(encoded_base_string);

// Generate str from base64-encoded bytestring hash.
string b64_str_hmac_hash = Convert.ToBase64String(K_hash);

// URL-encode the base64 hash str and add to oauth params dict.
oauth_params.Add("oauth_signature", EscapeUriDataStringRfc3986(b64_str_hmac_hash));
```
