### Prepend Copy Location

We can find the prepend by first converting our access token secret to a bytestring. We then decrypt the bytestring using our private encryption key as an RSA key with PKCS1v1.5 padding. The prepend is the resulting bytestring converted to a hex string value.

- Python
- C#

```
# Replace with path to private encryption key file.
with open("./private_encrpytion.pem", "r") as f:
    encryption_key = RSA.importKey(f.read())

bytes_decrypted_secret = PKCS1_v1_5_Cipher.new(
    key=encryption_key
    ).decrypt(
        ciphertext=base64.b64decode(access_token_secret), 
        sentinel=None,
        )
prepend = bytes_decrypted_secret.hex()
```

```
// Create the crypto provider 
RSACryptoServiceProvider bytes_decrypted_secret = new()
{
  // Utililze a keysize of 2048 rather than the default 7168
  KeySize = 2048
};

StreamReader sr = new("./private_encryption.pem");
string reader = sr.ReadToEnd();
sr.Close();

// Find the pem field content from the StreamReader string
PemFields pem_fields = PemEncoding.Find(reader);

// Convert the pem base 64 string content into a byte array for use in our import
byte[] der_data = Convert.FromBase64String(reader[pem_fields.Base64Data]);

// Import the bytes object as our key
bytes_decrypted_secret.ImportPkcs8PrivateKey(der_data, out _);

// Encode the access token secret as an ASCII bytes object
byte[] encryptedSecret = Convert.FromBase64String(access_token_secret);

// Decrypt our secret bytes with the encryption key
byte[] raw_prepend = bytes_decrypted_secret.Decrypt(encryptedSecret, RSAEncryptionPadding.Pkcs1);

// Convert our bytestring to a hexadecimal string
string prepend = Convert.ToHexString(raw_prepend).ToLower();
```
