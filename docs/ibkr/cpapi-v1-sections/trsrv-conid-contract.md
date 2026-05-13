### Search the security definition by Contract ID Copy Location

Returns a list of security definitions for the given conids

`GET /trsrv/secdef`

#### Request Object

###### Query Prams

**conids:** int\*. Required  
 A comma separated series of contract IDs.  
 Value Format: 1234

- Python
- cURL

```
request_url = f"{baseUrl}/trsrv/secdef?conids=265598"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/trsrv/secdef?conids=265598 \
--request GET
```

#### Response Object

**secdef**: array.  
 Returns the contents of the request with the array.

**conid:** int.  
 Returns the conID

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

**incrementRules & displayRule:** Array.  
 Returns rules regarding incrementation for order placement. Not functional for all exchanges. Please see [/iserver/contract/rules](/campus/ibkr-api-page/cpapi-v1/#rules-contract) for more accurate rule details.

**isEventContract:** bool.  
 Returns if the contract is an event contract or not.

**pageSize:** int.  
 Returns the content size of the request.

```
{
  "secdef": [
    {
      "conid": 265598,
      "currency": "USD",
      "time": 43,
      "chineseName": "苹果公司",
      "allExchanges": "AMEX,NYSE,CBOE,PHLX,CHX,ARCA,ISLAND,ISE,IDEAL,NASDAQQ,NASDAQ,DRCTEDGE,BEX,BATS,NITEECN,EDGEA,CSFBALGO,JEFFALGO,NYSENASD,PSX,BYX,ITG,PDQ,IBKRATS,CITADEL,NYSEDARK,MIAX,IBDARK,CITADELDP,NASDDARK,IEX,WEDBUSH,SUMMER,WINSLOW,FINRA,LIQITG,UBSDARK,BTIG,VIRTU,JEFF,OPCO,COWEN,DBK,JPMC,EDGX,JANE,NEEDHAM,FRACSHARE,RBCALGO,VIRTUDP,BAYCREST,FOXRIVER,MND,NITEEXST,PEARL,GSDARK,NITERTL,NYSENAT,IEXMID,HRT,FLOWTRADE,HRTDP,JANELP,PEAK6,IMCDP,CTDLZERO,HRTMID,JANEZERO,HRTEXST,IMCLP,LTSE,SOCGENDP,MEMX,INTELCROS,VIRTUBYIN,JUMPTRADE,NITEZERO,TPLUS1,XTXEXST,XTXDP,XTXMID,COWENLP,BARCDP,JUMPLP,OLDMCLP,RBCCMALP,WALLBETH,IBEOS,JONES,GSLP,BLUEOCEAN,USIBSILP,OVERNIGHT,JANEMID,IBATSEOS,HRTZERO,VIRTUALGO",
      "listingExchange": "NASDAQ",
      "countryCode": "US",
      "name": "APPLE INC",
      "assetClass": "STK",
      "expiry": null,
      "lastTradingDay": null,
      "group": "Computers",
      "putOrCall": null,
      "sector": "Technology",
      "sectorGroup": "Computers",
      "strike": "0",
      "ticker": "AAPL",
      "undConid": 0,
      "multiplier": 0.0,
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
}
```
