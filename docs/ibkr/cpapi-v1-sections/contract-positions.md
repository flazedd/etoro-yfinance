### Positions by Conid Copy Location

Returns a list containing position details only for the specified conid.

The initial request will return exclusively the Portfolio information on the contract. Sequential requests for the contract will also return the contract’s information and rules as shown below.

`GET /portfolio/{acctId}/position/{conid}`

#### Request Object

###### Path Params

**accountId:** String. Required  
 The account ID for which account should place the order.

**conId:** String. Required  
 The contract ID to receive position information on.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/U1234567/position/265598"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/U1234567/position/265598 \
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
    "mktPrice": 197.3840027,
    "mktValue": 121245.87,
    "currency": "USD",
    "avgCost": 192.7477563,
    "avgPrice": 192.7477563,
    "realizedPnl": 0.0,
    "unrealizedPnl": 2847.88,
    "exchs": null,
    "expiry": null,
    "putOrCall": null,
    "multiplier": 0.0,
    "strike": "0",
    "exerciseStyle": null,
    "conExchMap": [],
    "assetClass": "STK",
    "undConid": 0,
    "model": "",
    "time": 43,
    "chineseName": "苹果公司",
    "allExchanges": "AMEX,NYSE,CBOE,PHLX,CHX,ARCA,ISLAND,ISE,IDEAL,NASDAQQ,NASDAQ,DRCTEDGE,BEX,BATS,NITEECN,EDGEA,CSFBALGO,JEFFALGO,NYSENASD,PSX,BYX,ITG,PDQ,IBKRATS,CITADEL,NYSEDARK,MIAX,IBDARK,CITADELDP,NASDDARK,IEX,WEDBUSH,SUMMER,WINSLOW,FINRA,LIQITG,UBSDARK,BTIG,VIRTU,JEFF,OPCO,COWEN,DBK,JPMC,EDGX,JANE,NEEDHAM,FRACSHARE,RBCALGO,VIRTUDP,BAYCREST,FOXRIVER,MND,NITEEXST,PEARL,GSDARK,NITERTL,NYSENAT,IEXMID,HRT,FLOWTRADE,HRTDP,JANELP,PEAK6,IMCDP,CTDLZERO,HRTMID,JANEZERO,HRTEXST,IMCLP,LTSE,SOCGENDP,MEMX,INTELCROS,VIRTUBYIN,JUMPTRADE,NITEZERO,TPLUS1,XTXEXST,XTXDP,XTXMID,COWENLP,BARCDP,JUMPLP,OLDMCLP,RBCCMALP,WALLBETH,IBEOS,JONES,GSLP,BLUEOCEAN,USIBSILP,OVERNIGHT,JANEMID,IBATSEOS,HRTZERO,VIRTUALGO",
    "listingExchange": "NASDAQ",
    "countryCode": "US",
    "name": "APPLE INC",
    "lastTradingDay": null,
    "group": "Computers",
    "sector": "Technology",
    "sectorGroup": "Computers",
    "ticker": "AAPL",
    "type": "COMMON",
    "hasOptions": true,
    "fullName": "AAPL",
    "isUS": true,
    "incrementRules": [
      {
        "lowerEdge": 0.0,
        "increment": 0.01
      }
    ],
    "displayRule": {
      "magnification": 0,
      "displayRuleStep": [
        {
          "decimalDigits": 2,
          "lowerEdge": 0.0,
          "wholeDigits": 4
        }
      ]
    },
    "isEventContract": false,
    "pageSize": 100
  }
]
```
