### Calculating K Copy Location

To calculate our live session token, we need to use modulus division to receive a K value for a HMAC hash.

Begin by pulling the base value, B, which will be our dh\_response value from our /live\_session\_token response, using a leading 0 as a sign bit for the hex string.

We will then need to retrieve a BigInteger value of the dh\_response value.

Our exponent value would be equivalent to the same dh\_random value used for our /live\_session\_token request.

Our modulus, p, would be the same as our dh\_modulus or dh\_prime value from our Diffie-Hellman file.

We would finally calculate K using the formula B^a modulo p.

- Python
- C#

```
# K will be used to hash the prepend bytestring (the decrypted access token) to produce the LST.
B = int(dh_response, 16)
a = dh_random
p = dh_prime
K = pow(B, a, p)
```

```
// Validate that our dh_response value has a leading sign bit, and if it's not there then be sure to add it.
if (dh_response[0] != 0)
{
    dh_response = "0" + dh_response;
}

// Convert our dh_response hex string to a biginteger. 
BigInteger B = BigInteger.Parse(dh_response, NumberStyles.HexNumber);

BigInteger a = dh_random;
BigInteger p = dh_modulus;

// K will be used to hash the prepend bytestring (the decrypted access token) to produce the LST.
BigInteger K = BigInteger.ModPow(B, a, p);
```

Once K is receive, convert the integer to its hex string representation before converting it to a byte array. In some cases, the resultant K value will have an odd number of leading characters that should be prepended by an additional 0.

- Python
- C#

```
# Generate hex string representation of integer K.
hex_str_K = hex(K)[2:]

# If hex string K has odd number of chars, add a leading 0, because all Python hex bytes must contain two hex digits  (0x01 not 0x1).
if len(hex_str_K) % 2:
    print("adding leading 0 for even number of chars")
    hex_str_K = "0" + hex_str_K

# Generate hex bytestring from hex string K.
hex_bytes_K = bytes.fromhex(hex_str_K)

# Prepend a null byte to hex bytestring K if lacking sign bit.
if len(bin(K)[2:]) % 8 == 0:
    hex_bytes_K = bytes(1) + hex_bytes_K
```

```
// Generate hex string representation of integer K. Be sure to strip the leading sign bit.
string hex_str_k = K.ToString("X").ToLower(); // It must be converted to lowercase values prior to byte conversion.

// If hex string K has odd number of chars, add a leading 0
if (hex_str_k.Length % 2 != 0)
{
    // Set the lead byte to 0 for a positive sign bit.
    hex_str_k = "0" + hex_str_k;
}

// Generate hex bytestring from hex string K.
byte[] hex_bytes_K = Convert.FromHexString(hex_str_k);
```
