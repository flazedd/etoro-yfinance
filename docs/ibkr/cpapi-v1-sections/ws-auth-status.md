### Authentication Status Copy Location

When initially connecting to the websocket endpoint, the topic sts will relay back the current authentication status of the user. Authentication status updates, for example those resulting from competing sessions, are also relayed back to the websocket client via this topic.

**topic:** String.  
 Returns the topic of the given request.

**args:** Object.  
 Returns the data object.

**authenticated****:** bool.  
 Returns whether the user is authenticated to the brokerage session.

```
{
    "topic": "sts" ,
    "args": {
        "authenticated": authenticated
    }
}
```
