### Search Contract Rules Copy Location

Returns trading related rules for a specific contract and side.

`POST /iserver/contract/rules`

#### Request Object

###### Body Parameters

**conid:** Number. Required  
 Contract identifier for the interested contract.

**exchange:** String.  
 Designate the exchange you wish to receive information for in relation to the contract.

**isBuy:** bool.  
 Side of the market rules apply too. Set to true for Buy Orders, set to false for Sell Orders  
 Defaults to true or Buy side rules.

**modifyOrder:** bool.  
 Used to find trading rules related to an existing order.

**orderId:** Number. Required for modifyOrder:true  
 Specify the order identifier used for tracking a given order.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/contract/rules"
json_content = {
  "conid": 265598,
  "exchange": "SMART",
  "isBuy": true,
  "modifyOrder": true,
  "orderId": 1234567890
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/iserver/contract/rules \
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "conid": 265598,
  "exchange": "SMART",
  "isBuy": true,
  "modifyOrder": true,
  "orderId": 1234567890
}'
```

#### Response Object

**algoEligible:** bool.  
 Indicates if the contract can trade algos or not.

**overnightEligible:** bool.  
 Indicates if outsideRTH trading is permitted for the instrument

**costReport:** bool.  
 Indicates whether or not a cost report has been requested (Client Portal only).

**canTradeAcctIds:** Array of Strings.  
 Indicates permitted accountIDs that may trade the contract.

**error:** String.  
 If rules information can not be received for any reason, it will be expressed here.

**orderTypes:** Array of Strings  
 Indicates permitted order types for use with standard quantity trading.

**ibAlgoTypes:** Array of Strings.  
 Indicates permitted algo types for use with the given contract.

**fraqTypes:** Array of Strings.  
 Indicates permitted order types for use with fractional trading.

**forceOrderPreview:** bool.  
 Indicates if the order preview is forced upon the user before submission.

**cqtTypes:** Array of Strings.  
 Indicates accepted order types for use with cash quantity.

**orderDefaults:** Object of objects  
 Indicates default order type for the given security type.

**orderTypesOutside:** Array of Strings.  
 Indicates permitted order types for use outside of regular trading hours.

**defaultSize:** int.  
 Default total quantity value for orders.

**cashSize:** float.  
 Default cash value quantity.

**sizeIncrement:** int.  
 Indicates quantity increase for the contract.

**tifTypes:** Array of Strings.  
 Indicates allowed tif types supported for the contract.

**tifDefaults:** Object.  
 Object containing details about your TIF value defaults.  
 These defaults can be viewed and modified in TWS’s within the Global Configuration.

**limitPrice:** float.  
 Default limit price for the given contract.

**stopprice:** float.  
 Default stop price for the given contract.

**orderOrigination:** String.  
 Order origin designation for US securities options and Options Clearing Corporation

**preview:** bool.  
 Indicates if the order preview is required (for client portal only)

**displaySize:** int.

**fraqInt:** int.  
 Indicates decimal places for fractional order size

**cashCcy:** String.  
 Indicates base currency for the instrument.

**cashQtyIncr:** int.  
 Indicates cash quantity increment rules.

**priceMagnifier:** int.  
 Signifies if a contract is not trading in the standard cash denomination.  
 If a symbol is priced in Cents, Pence, or the currency’s fractional equivalent, the relative value will be displayed. For standard instruments, Null will be passed.

**negativeCapable:** bool.  
 Indicates if the value of the contract can be negative (true) or if it is always positive (false).

**incrementType:** int.  
 Indicates the type of increment style.

**incrementRules:** Array of objects.  
 Indicates increment rule values including lowerEdge and increment value.

**hasSecondary:** bool.

**modTypes:** Array of Strings.  
 Lists the available order types supported when modifying the order.

**increment:** float.  
 Minimum increment values for prices

**incrementDigits:** int.  
 Number of decimal places to indicate the increment value.

```
{
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
  "fraqTypes": [],
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
      "LP": "549000.00"
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
  "sizeIncrement": 1,
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
  "limitPrice": 549000.0,
  "stopprice": 549000.0,
  "orderOrigination": null,
  "preview": true,
  "displaySize": null,
  "fraqInt": 0,
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
```
