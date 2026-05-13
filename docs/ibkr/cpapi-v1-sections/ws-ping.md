### Ping Session Copy Location

#### Websocket Ping request

###### Topic:

**tic**  
 Ping the websocket in order to keep the websocket session alive.  
 To maintain a session for accessing /iserver or /ccp endpoints, use the topic **tic**. It is advised to ping the session at least once per minute.

**Note:** It is still required to send a request to the /tickle endpoint every few minutes or when the session expires (/sso/validate is returning a 0).

Do not pass arguments

```
tic
```
