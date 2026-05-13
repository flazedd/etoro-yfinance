### Combination Positions Copy Location

Provides all positions held in the account acquired as a combination, including values such as ratios, size, and market value.

`GET /portfolio/{accountId}/combo/positions`

#### Request Object

###### Path Params

**accountId:** String. Required  
 The account ID for which account should place the order.

###### Query Param

**nocache:** Boolean  
 Set if request should be made without caching.  
 Defaults to false

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/U1234567/combo/positions?nocache=true"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/U1234567/combo/positions?nocache=true \
--request GET
```

#### Response Object

**name:** String.  
 This is an internal name used to distinguish between combinations.

**description:** String.  
 Provides the ratio and leg conIds for the combo.

**legs:** array.  
 An array containing all legs in the specific combination.

**conid:** String.  
 Returns the conid of one leg of the combo.

**ratio:integer  
 Returns the ratio value for the combo. This can be either positive or negative.**

**positions:** array.  
 Provides an array including the leg information in the combo.

**acctId:** String.  
 Returns the accountId holding the leg.

conid: integer.  
 Returns the contract ID for the specific leg.

**contractDesc:** String.  
 Returns the long name for the given contract.

position: integer.  
 Returns the total size of the specific leg in the combination.

mktPrice: integer.  
 Returns the current market price of each share for the leg in the combo.

mktValue: integer.  
 Returns the total value of the position in the combo.

currency: String.  
 Returns the base currency of the leg.

avgCost: integer.  
 Returns the average cost of each share in the position times the multiplier.

avgPrice: integer.  
 Returns the average cost of each share in the position when purchased.

realizedPnl: integer.  
 Returns the total profit made today through trades.

**unrealizedPnl:** integer.  
 Returns the total potential profit if you were to trade.

**exchs:** null.  
 Deprecated value.  
 Always returns null.

**expiry:** null.  
 Deprecated value.  
 Always returns null.

**putOrCall:** null.  
 Deprecated value.  
 Always returns null.

**multiplier:** null.  
 Deprecated value.  
 Always returns null.

**strike:** integer.  
 Deprecated value.  
 Always returns 0.0.

exerciseStyle: null.  
 Deprecated value.  
 Always returns null.

**conExchMap:** array.  
 Deprecated value.  
 Returns an empty array.

**assetClass:** String.  
 Returns the security type of the leg.

**undConid:** integer  
 Deprecated value.  
 Always returns 0.

```
[
  {
    "name":"CP.CP66a00d50",
    "description":"1*708474422-1*710225103",
    "legs":[
      {
        "conid":"708474422",
        "ratio":1
      },
      {
        "conid":"710225103",
        "ratio":-1
      }
    ],
    "positions":[
      {
        "acctId":"U1234567",
        "conid":708474422,
        "contractDesc":"SPX AUG2024 5555 P [SPX 240816P05555000 100]",
        "position":1.0,
        "mktPrice":59.6571617,
        "mktValue":5965.72,
        "currency":"USD",
        "avgCost":6011.70935,
        "avgPrice":60.1170935,
        "realizedPnl":0.0,
        "unrealizedPnl":-45.99,
        "exchs":null,
        "expiry":null,
        "putOrCall":null,
        "multiplier":null,
        "strike":0.0,
        "exerciseStyle":null,
        "conExchMap":[],
        "assetClass":"OPT",
        "undConid":0
      },
      {
        "acctId":"U1234567",
        "conid":710225103,
        "contractDesc":"SPX AUG2024 5565 C [SPX 240816C05565000 100]",
        "position":-1.0,
        "mktPrice":78.02521515,
        "mktValue":-7802.52,
        "currency":"USD",
        "avgCost":7628.29065,
        "avgPrice":76.2829065,
        "realizedPnl":0.0,
        "unrealizedPnl":-174.23,
        "exchs":null,"expiry":null,
        "putOrCall":null,
        "multiplier":null,
        "strike":0.0,
        "exerciseStyle":null,
        "conExchMap":[],
        "assetClass":"OPT",
        "undConid":0
      }
    ]
  }
]
```
