### Encoded Base String Copy Location

The Encoded Base String for the Live Session Token is composed of the Prepend, Method, “&”, URL, “&”, and OAuth params combined as a sorted string.

Both the URL and the parameter string **must** be URI escaped according to [Rfc3986](https://datatracker.ietf.org/doc/html/rfc3986).

- Python
- C#

```
params_string = "&".join([f"{k}={v}" for k, v in sorted(oauth_params.items())])
method = 'POST'
url = f'https://{baseUrl}/oauth/live_session_token'
base_string = f"{prepend}{method}&{quote_plus(url)}&{quote(params_string)}"
encoded_base_string = base_string.encode("utf-8")
```

```
// Sort our oauth_params dictionary by key.
Dictionary<string, string> sorted_params = oauth_params.OrderBy(pair => pair.Key).ToDictionary(pair => pair.Key, pair => pair.Value);

// Combine our oauth_params into a single string for our base_string.
string params_string = string.Join("&", sorted_params.Select(kv => $"{kv.Key}={kv.Value}"));

// Create a base string by combining the prepend, url, and params string.
string base_string = $"{prepend.ToLower()}POST&{EscapeUriDataStringRfc3986(lst_url)}&{EscapeUriDataStringRfc3986(params_string)}";

// Convert our new string to a bytestring 
byte[] encoded_base_string = Encoding.UTF8.GetBytes(base_string);
```
