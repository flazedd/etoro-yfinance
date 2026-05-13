### Cancel Price Ladder Subscription Copy Location

#### Cancel Price Ladder Request

###### Topic:

**ubd**  
 Unsubscribes the user from price ladder data.

###### Arguments:

**acctId:** Required.  
 Must pass the account ID of the account that made the request.

```
ubd+{acctId}
```

#### Price Ladder Unsubscribe Response

No response is returned upon unsubscribing from the price ladder. There will just be an end to the data stream for the given acctId and the user may subscribe to a new price ladder source.
