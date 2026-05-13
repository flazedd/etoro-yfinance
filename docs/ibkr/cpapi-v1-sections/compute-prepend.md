### Prepend Bytes Copy Location

We first need to convert our Prepend hex string value into bytes. This will be used to generate a HMAC Hash later.

- Python
- C#

```
# Generate bytestring from prepend hex str.
prepend_bytes = bytes.fromhex(prepend)
```

```
//Generate bytestring from prepend hex str.
byte[] prepend_bytes = Convert.FromHexString(prepend);
```
