### Send a Websocket Topic Copy Location

After establishing your session, you may send whichever topics are needed through the newly established websocket.

- Python
- cURL

```
on_open(ws):
    print("Opened Connection")
    time.sleep(3)
    ws.send('smd+265598+{"fields":["31","84","86"]}')
```

Please note that while the websocket session itself supports the ability to establish a websocket, cURL is unable to send future topic requests. This would need to be facilitated by either a third party terminal add-on, or a programming language such as Python, Java, or otherwise.
