### Find all Info and Rules for a given contract Copy Location

Returns both contract info and rules from a single endpoint.  
 For only contract rules, use the endpoint /iserver/contract/rules.  
 For only contract info, use the endpoint /iserver/contract/{conid}/info.

`GET /iserver/contract/{{ conid }}/info-and-rules`

#### Request Object

###### Path Parameters

**coind:** String. Required  
 Contract identifier for the given contract.

###### Query Parameters

**isBuy:** bool.  
 Indicates whether you are searching for Buy or Sell order rules.  
 Set to true for Buy Orders, set to false for Sell Orders

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/contract/265598/info-and-rules?isBuy=true"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/contract/265598/info-and-rules?isBuy=true \ 
--request GET
```

#### Response Object

**cfi\_code:** String.  
 Classification of Financial Instrument codes

**symbol:** String.  
 Underlying symbol

**cusip:** String.  
 Returns the CUSIP for the given instrument.  
 Only used in BOND trading.

**expiry\_full:** String.  
 Returns the expiration month of the contract.  
 Formatted as “YYYYMM”

**con\_id:** int.  
 Indicates the contract identifier of the given contract.

**maturity\_date:** String.  
 Indicates the final maturity date of the given contract.  
 Formatted as “YYYYMMDD”

**industry:** String.  
 Specific group of companies or businesses.

**instrument\_type:** String.  
 Asset class of the instrument.

**trading\_class:** String.  
 Designated trading class of the contract.

**valid\_exchanges:** String.  
 Comma separated list of support exchanges or trading venues.

**allow\_sell\_long:** bool.  
 Allowed to sell shares you own.

**is\_zero\_commission\_security:** bool.  
 Indicates if the contract supports zero commission trading.

**local\_symbol:** String.  
 Contract’s symbol from primary exchange. For options it is the OCC symbol.

**contract\_clarification\_type:** null

**classifier:** null.

**currency:** String.  
 Base currency contract is traded in.

**text:** String.  
 Indicates the display name of the contract, as shown with Client Portal.

**underlying\_con\_id:** int.  
 Underlying contract identifier for the requested contract.

**r\_t\_h:** bool.  
 Indicates if the contract can be traded outside regular trading hours or not.

**multiplier:** String.  
 Indicates the multiplier of the contract.

**underlying\_issuer:** String.  
 Indicates the issuer of the underlying.

**contract\_month:** String.  
 Indicates the year and month the contract expires.  
 Value Format: “YYYYMM”

**company\_name:** String.  
 Indicates the name of the company or index.

**smart\_available:** bool.  
 Indicates if the contract can be smart routed or not.

**exchange:** String.  
 Indicates the primary exchange for which the contract can be traded.

**category:** String.  
 Indicates the industry category of the instrument.

**rules:** Object.  
 [See the `/iserver/contract/rules`](/campus/ibkr-api-page/cpapi-v1/#rules-contract) [endpoint.](/campus/ibkr-api-page/cpapi-v1/#rules-contract)

```
{
  "cfi_code": "",
  "symbol": "AAPL",
  "cusip": null,
  "expiry_full": null,
  "con_id": 265598,
  "maturity_date": null,
  "industry": "Computers",
  "instrument_type": "STK",
  "trading_class": "NMS",
  "valid_exchanges": "SMART,AMEX,NYSE,CBOE,PHLX,ISE,CHX,ARCA,ISLAND,DRCTEDGE,BEX,BATS,EDGEA,JEFFALGO,BYX,IEX,EDGX,FOXRIVER,PEARL,NYSENAT,LTSE,MEMX,TPLUS1,IBEOS,OVERNIGHT,PSX",
  "allow_sell_long": false,
  "is_zero_commission_security": false,
  "local_symbol": "AAPL",
  "contract_clarification_type": null,
  "classifier": null,
  "currency": "USD",
  "text": null,
  "underlying_con_id": 0,
  "r_t_h": true,
  "multiplier": null,
  "underlying_issuer": null,
  "contract_month": null,
  "company_name": "APPLE INC",
  "smart_available": true,
  "exchange": "SMART",
  "category": "Computers",
  "rules": {
    "algoEligible": true,
    "overnightEligible": true,
    "costReport": false,
    "canTradeAcctIds": [
      "U1234567"
    ],
    "error": null,
    "orderTypes": [
      "limit",
      "midprice",
      "market",
      "stop",
      "stop_limit",
      "mit",
      "lit",
      "trailing_stop",
      "trailing_stop_limit",
      "relative",
      "marketonclose",
      "limitonclose"
    ],
    "ibAlgoTypes": [
      "limit",
      "stop_limit",
      "lit",
      "trailing_stop_limit",
      "relative",
      "marketonclose",
      "limitonclose"
    ],
    "fraqTypes": [
      "limit",
      "market",
      "stop",
      "stop_limit",
      "mit",
      "lit",
      "trailing_stop",
      "trailing_stop_limit"
    ],
    "forceOrderPreview": false,
    "cqtTypes": [
      "limit",
      "market",
      "stop",
      "stop_limit",
      "mit",
      "lit",
      "trailing_stop",
      "trailing_stop_limit"
    ],
    "orderDefaults": {
      "LMT": {
        "LP": "197.93"
      }
    },
    "orderTypesOutside": [
      "limit",
      "stop_limit",
      "lit",
      "trailing_stop_limit",
      "relative"
    ],
    "defaultSize": 100,
    "cashSize": 0.0,
    "sizeIncrement": 100,
    "tifTypes": [
      "IOC/MARKET,LIMIT,RELATIVE,MARKETONCLOSE,MIDPRICE,LIMITONCLOSE,MKT_PROTECT,STPPRT,a",
      "GTC/o,a",
      "OPG/LIMIT,MARKET,a",
      "GTD/o,a",
      "DAY/o,a"
    ],
    "tifDefaults": {
      "TIF": "DAY",
      "SIZE": "100.00"
    },
    "limitPrice": 197.93,
    "stopprice": 197.93,
    "orderOrigination": null,
    "preview": true,
    "displaySize": null,
    "fraqInt": 4,
    "cashCcy": "USD",
    "cashQtyIncr": 500,
    "priceMagnifier": null,
    "negativeCapable": false,
    "incrementType": 1,
    "incrementRules": [
      {
        "lowerEdge": 0.0,
        "increment": 0.01
      }
    ],
    "hasSecondary": true,
    "increment": 0.01,
    "incrementDigits": 2
  }
}
```
