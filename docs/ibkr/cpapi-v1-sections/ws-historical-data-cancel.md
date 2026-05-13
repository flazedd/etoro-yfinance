### Cancel Historical Market Data Copy Location

#### Cancel Historical Data Request

###### Topic:

**umh**  
 Unubscribes the user from historical bar data.

###### Arguments:

serverId: String. Required

serverId is passed initially from the historical data request.

```
umh+{serverId}
```

#### Historical Data Unsubscribe Response

No response is returned upon unsubscribing from historical data. There will just be an end to the historical data stream for the given serverId and one of the five subscriptions will be available again.
