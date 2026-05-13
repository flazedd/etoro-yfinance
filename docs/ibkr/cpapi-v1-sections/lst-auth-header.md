### Authorization Header Copy Location

The Authorization Header compiles our full OAuth parameters into an alphabetically-sorted string.

- Each key/value pair must be added in the format ‘key=\”value\”, where each value is surrounded with quotes
- Each pair separated with a comma.
- The string must be prepended with “OAuth “.

The final string should be added as a header for your request using the “Authorization” header.

- Python
- C#

```
# Assemble oauth params into auth header value as comma-separated str.
oauth_header = "OAuth " + ", ".join([f'{k}="{v}"' for k, v in sorted(oauth_params.items())])

# Create dict for LST request headers including OAuth Authorization header.
headers = {"Authorization": oauth_header}
```

```
Dictionary fin_sorted_params = oauth_params.OrderBy(pair => pair.Key).ToDictionary(pair => pair.Key, pair => pair.Value);

// Assemble oauth params into auth header value as comma-separated str.
string oauth_header = $"OAuth " + string.Join(", ", fin_sorted_params.Select(kv => $"{kv.Key}=\"{kv.Value}\""));

// Add our Authorization header to our request's header container.
request.Headers.Add("Authorization", oauth_header);
```
