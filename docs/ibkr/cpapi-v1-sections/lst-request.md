### Request Copy Location

```
# Generate a random 256-bit integer.
dh_random = random.getrandbits(256)

# Compute the Diffie-Hellman challenge:
# generator ^ dh_random % dh_prime
# Note that IB always uses generator = 2.
# Convert result to hex and remove leading 0x chars.
dh_challenge = hex(pow(base=dh_generator, exp=dh_random, mod=dh_prime))[2:]
# --------------------------------
# Generate LST request signature.
# --------------------------------

# Generate the base string prepend for the OAuth signature:
#   Decrypt the access token secret bytestring using private encryption
#   key as RSA key and PKCS1v1.5 padding.
#   Prepend is the resulting bytestring converted to hex str.
bytes_decrypted_secret = PKCS1_v1_5_Cipher.new(
    key=encryption_key
    ).decrypt(
        ciphertext=base64.b64decode(access_token_secret), 
        sentinel=None,
        )
prepend = bytes_decrypted_secret.hex()

# Put prepend at beginning of base string str.
base_string = prepend
# Elements of the LST request so far.
method = 'POST'
url = f'https://{baseUrl}/oauth/live_session_token'
oauth_params = {
    "oauth_consumer_key": consumer_key,
    "oauth_nonce": hex(random.getrandbits(128))[2:],
    "oauth_timestamp": str(int(datetime.now().timestamp())),
    "oauth_token": access_token,
    "oauth_signature_method": "RSA-SHA256",
    "diffie_hellman_challenge": dh_challenge,
}

# Combined param key=value pairs must be sorted alphabetically by key
# and ampersand-separated.
params_string = "&".join([f"{k}={v}" for k, v in sorted(oauth_params.items())])

# Base string = method + url + sorted params string, all URL-encoded.
base_string += f"{method}&{quote_plus(url)}&{quote(params_string)}"

# Convert base string str to bytestring.
encoded_base_string = base_string.encode("utf-8")
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

# Oauth realm param omitted from signature, added to header afterward.
oauth_params["realm"] = realm

# Assemble oauth params into auth header value as comma-separated str.
oauth_header = "OAuth " + ", ".join([f'{k}="{v}"' for k, v in sorted(oauth_params.items())])

# Create dict for LST request headers including OAuth Authorization header.
headers = {"Authorization": oauth_header}

# Add User-Agent header, required for all requests. Can have any value.
headers["User-Agent"] = "python/3.11"

# Prepare and send request to /live_session_token, print request and response.
lst_request = requests.post(url=url, headers=headers)

# Check if request returned 200, proceed to compute LST if true, exit if false.
if not lst_request.ok:
    print(f"ERROR: Request to /live_session_token failed. Exiting...")
    raise SystemExit(0)

# Script not exited, proceed to compute LST.
response_data = lst_request.json()
dh_response = response_data["diffie_hellman_response"]
lst_signature = response_data["live_session_token_signature"]
lst_expiration = response_data["live_session_token_expiration"]
```
