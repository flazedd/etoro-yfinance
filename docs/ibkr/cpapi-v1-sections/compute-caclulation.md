### Final Live Session Calculation Copy Location

To calculate the Live Session Token, we need to create a new HMAC Sha1 object, using the K hex bytes as a key. We then hash our HMAC Sha1 object against our prepend byte string.

The final byte array, converted to a Base64 string, is the computed live session token.

- Python
- C#

```
bytes_hmac_hash_K = HMAC.new(
    key=hex_bytes_K,
    msg=prepend_bytes,
    digestmod=SHA1,
    ).digest()
# The computed LST is the base64-encoded HMAC hash of the hex prepend bytestring. Converted here to str.
computed_lst = base64.b64encode(bytes_hmac_hash_K).decode("utf-8")
```

```
// Create HMAC SHA1 object
HMACSHA1 bytes_hmac_hash_K = new()
{
    // Set the HMAC key to our passed intended_key byte array
    Key = hex_bytes_K
};
// Hash the SHA1 bytes of our key against the msg content.
byte[] K_hash = bytes_hmac_hash_K.ComputeHash(prepend_bytes);

// Convert hash to base64 to retrieve the computed live session token.
string computed_lst = Convert.ToBase64String(K_hash);
```
