### Request Copy Location

```
url = f'https://api.ibkr.com/v1/api/oauth/access_token'
oauth_params = {
  "oauth_callback":callback,
  "oauth_consumer_key": consumer_key,
  "oauth_nonce": hex(random.getrandbits(128))[2:],
  "oauth_signature_method": "RSA-SHA256",
  "oauth_timestamp": str(int(datetime.now().timestamp())),
  "oauth_token": rToken,
  "oauth_verifier": vToken,
  }
params_string = "&".join([f"{k}={v}" for k, v in sorted(oauth_params.items())])

# Base string successfully created
base_string = f"POST&{quote_plus(url)}&{quote(params_string)}"

# Base string should then signed with the private key in RSA-SHA256
encoded_base_string = base_string.encode("utf-8")
sha256_hash = SHA256.new(data=encoded_base_string)
bytes_pkcs115_signature = PKCS1_v1_5_Signature.new(
  rsa_key=signature_key
  ).sign(msg_hash=sha256_hash)
b64_str_pkcs115_signature = base64.b64encode(bytes_pkcs115_signature).decode("utf-8")

# Establish the authorization header
oauth_params["oauth_signature"] = quote_plus(b64_str_pkcs115_signature)
oauth_params["realm"] = realm
oauth_header = "OAuth " + ", ".join([f'{k}="{v}"' for k, v in sorted(oauth_params.items())])
headers = {"authorization": oauth_header}
headers["User-Agent"] = "python/3.11"

# Send the request and save the tokens to variables
atoken_request = requests.post(url=url, headers=headers)
aToken = atoken_request.json()["oauth_token"]
aToken_secret = atoken_request.json()["oauth_token_secret"]
```
