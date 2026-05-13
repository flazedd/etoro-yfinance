### OAuth Signature Copy Location

Creating the OAuth Signature is a multi-stage process.

1. First uses will need to create a sha256 hash of the encoded base string
2. Next, you will need to create a PKCS1 v1.5 ([Rfc2313](https://datatracker.ietf.org/doc/html/rfc2313)) bytestring signature using your Private Encryption Key as an RSA key to sign our sha256 hash value created in our prior step.
3. Once your bytestring has been generated, we will need to Base 64 encode our bytes, and then decode them using UTF-8 to receive a string value.
4. Finally, we will need to URI escape our string, again using [Rfc3986](https://datatracker.ietf.org/doc/html/rfc3986), to receive our final oauth\_signature value.

- Python
- C#

```
# Generate SHA256 hash of base string bytestring.
sha256_hash = SHA256.new(data=encoded_base_string)

# Generate bytestring PKCS1v1.5 signature of base string hash.
# RSA signing key is private signature key.
bytes_pkcs115_signature = PKCS1_v1_5_Signature.new(
    rsa_key=signature_key
    ).sign(msg_hash=sha256_hash)

# Generate str from base64-encoded bytestring signature.
b64_str_pkcs115_signature = base64.b64encode(bytes_pkcs115_signature).decode("utf-8")

# URL-encode the base64 signature str and add to oauth params dict.
oauth_params['oauth_signature'] = quote_plus(b64_str_pkcs115_signature)
```

```
// Create a Sha256 Instance
SHA256 sha256_inst = SHA256.Create();

// Generate SHA256 hash of base string bytestring.
byte[] sha256_hash = sha256_inst.ComputeHash(encoded_base_string);

// Create the crypto provider for our signature
RSACryptoServiceProvider bytes_pkcs115_signature = new()
{
    // Utililze a keysize of 2048 rather than the default 7168
    KeySize = 2048
};

// Use our function to retrieve the object bytes
StreamReader sr = new(signature_fp);
string reader = sr.ReadToEnd();
sr.Close();

// Find the pem field content from the StreamReader string
PemFields pem_fields = PemEncoding.Find(reader);

// Convert the pem base 64 string content into a byte array for use in our import
byte[] sig_der_data = Convert.FromBase64String(reader[pem_fields.Base64Data]);

// Import the bytes object as our key
bytes_pkcs115_signature.ImportPkcs8PrivateKey(sig_der_data, out _);

//Generate the Pkcs115 signature key
RSAPKCS1SignatureFormatter rsaFormatter = new(bytes_pkcs115_signature);

rsaFormatter.SetHashAlgorithm("SHA256");

//Receive the bytestring of our signature
byte[] signedHash = rsaFormatter.CreateSignature(sha256_hash);

// Convert the bytestring signature to base64.
string b64_str_pkcs115_signature = Convert.ToBase64String(signedHash);

// URL-encode the base64 signature str and add to oauth params dict.
oauth_params.Add("oauth_signature", EscapeUriDataStringRfc3986(b64_str_pkcs115_signature));
```
