### Position & Contract Info Copy Location

Returns an object containing information about a given position along with its contract details.

`GET /portfolio/positions/{conid}`

#### Request Object

###### Path Params

**conId:** String. Required  
 The contract ID to receive position information on.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/positions/265598"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/positions/265598 \
--request GET
```

#### Response Object

**accountId:** String.  
 Displays the accountId returning data for.

**acctId:** String.  
 Displays the accountId to return data for.

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

**strike:** int.  
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
 Retrns average decimal digit for data display.

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
    "conid": 265598,
    "contractDesc": "AAPL",
    "position": 614.2639,
    "mktPrice": 197.7639923,
    "mktValue": 121479.28,
    "currency": "USD",
    "avgCost": 192.7477563,
    "avgPrice": 192.7477563,
    "realizedPnl": 0.0,
    "unrealizedPnl": 3081.29,
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
