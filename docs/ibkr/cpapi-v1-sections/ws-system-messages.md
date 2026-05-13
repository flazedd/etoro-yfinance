### System Connection Messages Copy Location

When initially connecting to websocket the topic system relays back a confirmation with the corresponding username. While the websocket is connecting every 10 seconds there after a heartbeat with corresponding unix time (in millisecond format) is relayed back.

**topic:** String.  
 Returns the topic of the given request.

**success:** String.  
 Returns the username logged in with that has built the websocket.

```
{
    "topic": "system" ,
    "success": "success"
}
```
