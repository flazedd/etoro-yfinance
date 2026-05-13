### Establishing the Websocket with OAuth Copy Location

The process for those authenticating with OAuth is similar, though slightly different. In addition to the API cookie, you must also include the “oauth\_token” query param which should be set to the user’s access token value.

- Python
- cURL

```
ws = websocket.WebSocketApp(
  url="wss://api.ibkr.com/v1/api/ws?oauth_token={accessToken}",
  on_open=on_open,
  on_message=on_message,
  on_error=on_error,
  on_close=on_close,
  cookie=f"api={sessionToken}"
)
ws.run_forever()
```

```
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "origin: interactivebrokers.github.io" --cookie "api=d21b8cf5ebc8ea01c6ce37c8125ec83f" wss://api.ibkr.com/v1/api/ws?oauth_token={Access Token}
```
