### Establishing the Websocket with Client Portal Gateway Copy Location

Next, you will need to build your websocket to wss://localhost:5000/v1/api/ws. In your request to establish the websocket, be sure to set your cookie header as “api={‘session’ value here}”

- Python
- cURL

```
ws = websocket.WebSocketApp(
  url="wss://localhost:5000/v1/api/ws",
  on_open=on_open,
  on_message=on_message,
  on_error=on_error,
  on_close=on_close,
  cookie=f"api={sessionToken}"
)
ws.run_forever()
```

```
curl -i -k -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "origin: interactivebrokers.github.io" --cookie "api=d21b8cf5ebc8ea01c6ce37c8125ec83f" wss://localhost:5000/v1/api/ws
```
