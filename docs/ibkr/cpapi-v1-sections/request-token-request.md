### Request Copy Location

```
url = f'https://api.ibkr.com/v1/api/oauth/request_token'
oauth_params = {
  "oauth_callback": {{oauth_callback }},
  "oauth_consumer_key": {{consumer_key}},
  "oauth_nonce": hex(random.getrandbits(128))[2:],
  "oauth_signature_method": "RSA-SHA256",
  "oauth_timestamp": str(int(datetime.now().timestamp())),
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
  
request_request = requests.post(url=url, headers=headers)
if request_request.status_code == 200:
    rToken = request_request.json()["oauth_token"]
```
