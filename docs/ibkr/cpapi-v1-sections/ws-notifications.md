### Notifications Copy Location

If there is a brief message regarding trading activity the topic ntf will be sent.

**topic:** String.  
 Returns the topic of the given request.

**args:** Object.  
 Returns the object containing the pnl data.

**id:** String.  
 Returns the identifier for the specific notification.

**text:** String.  
 Returns the body text for the affiliated notification.

**title:** String.  
 Returns the title or headline for the notification.

**url:** String.  
 If relevant, provides a url where a user can go to read more about the notification.

```
{
    "topic": "ntf",
    "args": {
        "id": "id",
        "text": "text",
        "title": "title",
        "url": "url"
    }
}
```
