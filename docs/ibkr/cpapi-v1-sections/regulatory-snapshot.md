### Regulatory Snapshot Copy Location

**WARNING:** Each regulatory snapshot made **will incur a fee of $0.01 USD** to the account. **This applies to both live and paper accounts.**

If you are already paying for, or are subscribed to, a specific US Network subscription, your account will not be charged.

See [here](/campus/ibkr-api-page/market-data-subscriptions/#reg-snapshot) for more information about Regulatory Snapshots and Market Data.

Send a request for a regulatory snapshot.  
 **This will cost $0.01 USD per request**unless you are subscribed to the direct exchange market data already.

`GET /md/regsnapshot`

#### Request Object

###### Query Params

**conid:** String. Required  
 Provide the contract identifier to retrieve market data for.

- Python
- cURL

```
request_url = f"{baseUrl}/md/regsnapshot?conid=265598"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/md/regsnapshot?conid=265598 \
--request GET
```

#### Response Object

**Note:** The integer fields returned below also correspond to the [Market Data Field](#market-data-fields) values used for the standard /iserver/marketdata/snapshot endpoint.

**conid:** int.  
 Returns the contract ID of the request.

**conidEx:** String.  
 Returns the contract ID of the request type.

**BboExchange:** String.  
 Color for Best Bid/Offer Exchange in hex code

**HasDelayed:** false,  
 Returns if the data is live (false) or delayed (true).

**84:** float.  
 Returns the Bid value.

**86:** float.  
 Returns the Ask value.

**88:** int.  
 Returns the Bid size.

**85:** int.  
 Returns the Ask size.

**BestBidExch:** int.  
 Returns the exchange identifier of the current best bid value.  
 Internal use only.

**BestAskExch:** int.  
 Returns the exchange identifier of the current best Ask value.  
 Internal use only.

**31:** float.  
 Returns the exchange identifier of the most recent Last value.  
 Internal use only.

**7059:** int.  
 Returns the last traded size.

**LastExch:** int.  
 Returns the exchange of the last exchange as a binary integer\*  
 Internal use only.

**7057:** String.  
 Returns the series of character codes for the Ask exchange.

**7068:** String.  
 Returns the series of character codes for the Bid exchange.

**7058:** String.  
 Returns the series of character codes for the Last exchange.

```
{
  "conid": conid,
  "conidEx": "conidEx",
  "BboExchange": "BboExchange",
  "HasDelayed": HasDelayed,
  "84": "Bid",
  "86": "Ask",
  "88": Bid_Size,
  "85": Ask_Size,
  "BestBidExch": BestBidExch,
  "BestAskExch": BestAskExch,
  "31": "Last",
  "7059": Last_Size,
  "LastExch": LastExch,
  "7057": "Ask Exch",
  "7068": "Bid Exch",
  "7058": "Last_Exch"
}
```
