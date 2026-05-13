### Bracket Orders & OCA Groups Copy Location

The available values and structures of Bracket or OCA orders follow the same general structure of individual orders. Bracket and OCA orders require a parent order be submitted, and then each leg, or child order, would include the parent’s order ID.

Bracket orders can be submitted sequentially using the default order\_id created by Interactive Brokers.

OR

Bracket orders can be submitted using the cOID field for the parent order, and then use this same value in each of the child orders in the parentId field.

The body content on the right represents a standard bracket order which contains a parent order, a profit taker, and a stop loss. As you can see, the only addition to this order is the inclusion of cOID in the parent order, and the parentId field in the two children.

```
{
  "orders": [
    {
      "acctId": "U1234567",
      "conid": 265598,
      "cOID": "Parent",
      "orderType": "MKT",
      "listingExchange": "SMART",
      "outsideRTH": true,
      "side": "Buy",
      "referrer": "QuickTrade",
      "tif": "GTC",
      "quantity": 50
    },
    {
      "acctId": "U1234567",
      "conid": 265598,
      "orderType": "STP",
      "listingExchange": "SMART",
      "outsideRTH": false,
      "price": 157.30,
      "side": "Sell",
      "tif": "GTC",
      "quantity": 50,
      "parentId": "Parent"
    },
    {
      "acctId": "U1234567",
      "conid": 265598,
      "orderType": "LMT",
      "listingExchange": "SMART",
      "outsideRTH": false,
      "price": 157.00,
      "side": "Sell",
      "tif": "GTC",
      "quantity": 50,
      "parentId": "Parent"
    }
  ]
}
```

An OCA group will follow this same structure. However, in addition to the standard bracket, each order will include `"isSingleGroup": true`. Otherwise, no additional modifications need to be made.

```
{
  "orders": [
    {
      "acctId": "U1234567",
      "conid": 265598,
      "cOID": "Parent",
      "orderType": "MKT",
      "listingExchange": "SMART",
      "isSingleGroup": true,
      "outsideRTH": true,
      "side": "Buy",
      "referrer": "QuickTrade",
      "tif": "GTC",
      "quantity": 50
    },
    {
      "acctId": "U1234567",
      "conid": 265598,
      "orderType": "STP",
      "listingExchange": "SMART",
      "isSingleGroup": true,
      "outsideRTH": false,
      "price": 157.30,
      "side": "Sell",
      "tif": "GTC",
      "quantity": 50,
      "parentId": "Parent"
    },
    {
      "acctId": "U1234567",
      "conid": 265598,
      "orderType": "LMT",
      "listingExchange": "SMART",
      "outsideRTH": false,
      "isSingleGroup": true,
      "price": 157.00,
      "side": "Sell",
      "tif": "GTC",
      "quantity": 50,
      "parentId": "Parent"
    }
  ]
}
```
