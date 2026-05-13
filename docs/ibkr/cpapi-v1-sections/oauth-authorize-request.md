### Request Copy Location

For our programmatic implementation without an official callback url, we can introduce a simple line to direct the user to the login page and save the verifier token for later.

```
url = f'https://interactivebrokers.com/authorize?oauth_token={rToken}'
vToken = input(f"Please log in to {url} and paste the 'oauth_verifier' value here: ")
```
