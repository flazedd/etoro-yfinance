### Positions Copy Location

Returns a list of positions for the given account.  
 The endpoint supports paging, each page will return up to 100 positions.  
 /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint.

`GET /portfolio/{accountId}/positions/{pageId}`

#### Request Object

###### Path Params

**accountId:** String. Required  
 The account ID for which account should place the order.

**pageId:** String. Required  
 The “page” of positions that should be returned.  
 One page contains a maximum of 100 positions.  
 Pagination starts at 0.

###### Query Params

**model:** String.  
 Code for the model portfolio to compare against.

**sort:** String.  
 Declare the table to be sorted by which column

**direction:** String.  
 The order to sort by.  
 ‘a’ means ascending  
 ‘d’ means descending

**period:** String.  
 period for pnl column  
 Value Format: 1D, 7D, 1M

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/U1234567/positions/0?direction=a&period=1W&sort=position&model=MyModel"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/U1234567/positions/0?direction=a&period=1W&sort=position&model=MyModel \
--request GET
```

#### Response Object

**acctId:** String.

**conid:** int.  
 Returns the contract ID of the position.

**contractDesc:** String.  
 Returns the local symbol of the order.

**position:** float.  
 Returns the total size of the position.

**mktPrice:**  float.  
 Returns the current market price of each share.

**mktValue:**  float.  
 Returns the total value of the order.

**avgCost:** float.  
 Returns the average cost of each share in the position times the multiplier.

**avgPrice:** float.  
 Returns the average cost of each share in the position when purchased.

**realizedPnl:** float.  
 Returns the total profit made today through trades.

**unrealizedPnl:** float.  
 Returns the total potential profit if you were to trade.

**exchs:** null.  
 Deprecated value.  
 Always returns null.

**currency:** String.  
 Returns the traded currency for the contract.

**time:** int.  
 Returns amount of time in ms to generate the data.

**chineseName:** String.  
 Returns the Chinese characters for the symbol.

**allExchanges:** String\*.  
 Returns a series of exchanges the given symbol can trade on.

**listingExchange:** String.  
 Returns the primary or listing exchange the contract is hosted on.

**countryCode:** String.  
 Returns the country code the contract is traded on.

**name:** String.  
 Returns the comapny name.

**assetClass:** String.  
 Returns the asset class or security type of the contract.

**expiry:** String.  
 Returns the expiry of the contract. Returns null for non-expiry instruments.

**lastTradingDay:** String.  
 Returns the last trading day of the contract.

**group:** String.  
 Returns the group or industry the contract is affilated with.

**putOrCall:** String.  
 Returns if the contract is a Put or Call option.

**sector:** String.  
 Returns the contract’s sector.

**sectorGroup:** String.  
 Returns the sector’s group.

**strike:** String.  
 Returns the strike of the contract.

**ticker:** String.  
 Returns the ticker symbol of the traded contract.

**undConid:** int.  
 Returns the contract’s underlyer.

**multiplier:** float,  
 Returns the contract multiplier.

**type:** String.  
 Returns stock type.

**hasOptions:** bool.  
 Returns if contract has tradable options contracts.

**fullName:** String.  
 Returns symbol name for requested contract.

**isUS:** bool.  
 Returns if the contract is US based or not.

**incrementRules:** Array.  
 Returns rules regarding incrementation for market data and order placemnet.

**lowerEdge:** float,  
 Returns lower edge value used to calculate increment.

**increment:** float.  
 Allowed incrementable value.

**displayRule:** object.  
 Returns an object containing display content for market data.

**magnification:** int.  
 Returns maginification or multiplier of contract

**displayRuleStep:** Array.  
 Contains various rules in the display object.

**decimalDigits:** int.  
 Returns average decimal digit for data display.

**lowerEdge:** float.  
 Returns lower edge value used to calculate increment.

**wholeDigits:** int.  
 Returns allowed display size.

**isEventContract:** bool.  
 Returns if the contract is an event contract or not.

**pageSize:** int.  
 Returns the content size of the request.  
 }]

```
[
  {
    "acctId": "U1234567",
    "conid": 756733,
    "contractDesc": "SPY",
    "position": 5.0,
    "mktPrice": 471.16000365,
    "mktValue": 2355.8,
    "currency": "USD",
    "avgCost": 434.93,
    "avgPrice": 434.93,
    "realizedPnl": 0.0,
    "unrealizedPnl": 181.15,
    "exchs": null,
    "expiry": null,
    "putOrCall": null,
    "multiplier": null,
    "strike": 0.0,
    "exerciseStyle": null,
    "conExchMap": [],
    "assetClass": "STK",
    "undConid": 0,
    "model": ""
  },
  {
    "acctId": "U1234567",
    "conid": 76792991,
    "contractDesc": "TSLA",
    "position": 7.0,
    "mktPrice": 250.73399355,
    "mktValue": 1755.14,
    "currency": "USD",
    "avgCost": 221.67142855,
    "avgPrice": 221.67142855,
    "realizedPnl": 0.0,
    "unrealizedPnl": 203.44,
    "exchs": null,
    "expiry": null,
    "putOrCall": null,
    "multiplier": null,
    "strike": 0.0,
    "exerciseStyle": null,
    "conExchMap": [],
    "assetClass": "STK",
    "undConid": 0,
    "model": ""
  },
  {
    "acctId": "U1234567",
    "conid": 107113386,
    "contractDesc": "META",
    "position": 11.0,
    "mktPrice": 333.1199951,
    "mktValue": 3664.32,
    "currency": "USD",
    "avgCost": 306.6909091,
    "avgPrice": 306.6909091,
    "realizedPnl": 0.0,
    "unrealizedPnl": 290.72,
    "exchs": null,
    "expiry": null,
    "putOrCall": null,
    "multiplier": null,
    "strike": 0.0,
    "exerciseStyle": null,
    "conExchMap": [],
    "assetClass": "STK",
    "undConid": 0,
    "model": ""
  }
]
```
