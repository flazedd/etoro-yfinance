### Cancel Market Data Copy Location

#### Market Data Unsubscribe Request

###### Topic:

**umd**  
 Unubscribes the user from watchlist market data.

###### Topic Target:

**conids:** Required.  
 Must pass a single contract identifier.

###### Arguments:

null.

```
umd+conId+{}
```

#### Market Data Unsubscribe Response

No response is returned upon unsubscribing from market data. There will just be an end to the market data from the given conid.
