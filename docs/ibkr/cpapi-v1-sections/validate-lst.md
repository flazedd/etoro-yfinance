### Validate Live Session Token Copy Location

It should be noted that this step may be skipped for your final product, though it is essential during initial development stages to validate implementation.

After calculating our Live Session Token, the calculation may be validated through the following steps to re-calculate the lst\_signature value retrieved from the /live\_session\_token endpoint. If the calculated value matches the return value, then we have a valid live session token. If the two do not match, there is an issue in your LST generation process.

Begin by converting the computed live session token value to a base64 decoded byte array.

Next, retrieve the UTF-8 byte array equivalent of our consumer key.

Create a new HMAC Sha1 object, using the decoded live session token as a key. We then hash our HMAC Sha1 object against our consumer key byte string.

Convert the resultant byte array to a hex string.

If our new hex string matches the received lst\_signature value, then our computed\_lst value may be used as the live\_session\_token in future requests. If the two are different, then there may be an issue in the live\_session\_token generation process.

- Python
- C#

```
# Generate hex-encoded str HMAC hash of consumer key bytestring.
# Hash key is base64-decoded LST bytestring, method is SHA1.
hex_str_hmac_hash_lst = HMAC.new(
    key=base64.b64decode(computed_lst),
    msg=consumer_key.encode("utf-8"),
    digestmod=SHA1,
).hexdigest()

# If our hex hash of our computed LST matches the LST signature received in response, we are successful.
if hex_str_hmac_hash_lst == lst_signature:
    live_session_token = computed_lst
    print("Live session token computation and validation successful.")
    print(f"LST: {live_session_token}; expires: {datetime.fromtimestamp(lst_expiration/1000)}\n")
else:
    print(f"ERROR: LST validation failed.")
```

```
//Generate hex - encoded str HMAC hash of consumer key bytestring.
// Hash key is base64 - decoded LST bytestring, method is SHA1
byte[] b64_decode_lst = Convert.FromBase64String(computed_lst);

// Convert our consumer key str to bytes
byte[] consumer_bytes = Encoding.UTF8.GetBytes(consumer_key);

// Hash the SHA1 bytes against our hex bytes of K.
byte[] hashed_consumer = EasySha1(b64_decode_lst, consumer_bytes);

// Convert hash to base64 to retrieve the computed live session token.
string hex_lst_hash = Convert.ToHexString(hashed_consumer).ToLower();

// If our hex hash of our computed LST matches the LST signature received in response, we are successful.
if (hex_lst_hash == lst_signature)
{
    string live_session_token = computed_lst;
    Console.WriteLine("Live session token computation and validation successful.");
    Console.WriteLine($"LST: {live_session_token}; expires: {lst_expiration}\n");
}
else
{
    Console.WriteLine("######## LST MISMATCH! ########");
    Console.WriteLine($"Hexed LST: {hex_lst_hash} | LST Signature: {lst_signature}\n");
}
```
