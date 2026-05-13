### Positions (NEW) Copy Location

Returns a list of positions for the given account.  
 /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint.  
 This endpoint provides near-real time updates and removes caching otherwise found in the /portfolio/{accountId}/positions/{pageId} endpoint.

`GET /portfolio2/{accountId}/positions`

#### Request Object

###### Path Params

**accountId:** String. Required  
 The account ID for which account should place the order.

###### Query Params

**model:** String.  
 Code for the model portfolio to compare against.

**sort:** String.  
 Declare the table to be sorted by which column

**direction:** String.  
 The order to sort by.  
 ‘a’ means ascending  
 ‘d’ means descending

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio2/U1234567/positions?direction=a&sort=position"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio2/U1234567/positions?direction=a&sort=position \
--request GET
```

#### Response Object

**position:** float.  
 Returns the total size of the position.

**conid:** int.  
 Returns the contract ID of the position.

**avgCost:** float.  
 Returns the average cost of each share in the position times the multiplier.

**avgPrice:** float.  
 Returns the average cost of each share in the position when purchased.

**currency:** String.  
 Returns the traded currency for the contract.

**description:** String.  
 Returns the local symbol of the order.

**isLastToLoq:** String.  
 Returns if the contract is last to liquidate.

**mktPrice:**  float.  
 Returns the current market price of each share.

**mktValue:**  float.  
 Returns the total value of the order.

**realizedPnl:** float.  
 Returns the total profit made today through trades.

**unrealizedPnl:** float.  
 Returns the total potential profit if you were to trade.

**secType:** String.  
 Returns the asset class or security type of the contract.

**timestamp:** integer.  
 Returns the epoch timestamp of the portfolio request.

**assetClass:** String.  
 Returns the asset class or security type of the contract.

**sector:** String.  
 Returns the contract’s sector.

**group:** String.  
 Returns the group or industry the contract is affilated with.

**model**: String.  
 Code for the model portfolio to compare against.

{  
 “position”: 12.0,  
 “conid”: “9408”,  
 “avgCost”: 266.20888333333335,  
 “avgPrice”: 266.20888333333335,  
 “currency”: “USD”,  
 “description”: “MCD”,  
 “isLastToLoq”: false,  
 “marketPrice”: 258.8299865722656,  
 “marketValue”: 3105.9598388671875,  
 “realizedPnl”: 0.0,  
 “secType”: “STK”,  
 “timestamp”: 1717444668,  
 “unrealizedPnl”: 88.54676113281266,  
 “assetClass”: “STK”,  
 “sector”: “Consumer, Cyclical”,  
 “group”: “Retail”,  
 “model”: “”  
 }
