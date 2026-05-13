### Contract information by Contract ID Copy Location

Requests full contract details for the given conid

`GET /iserver/contract/{conid}/info`

#### Request Object

###### Path Params:

**conid:** String.  
 Contract ID for the desired contract information.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/contract/265598/info"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/contract/265598/info \ 
--request GET
```

#### Response Object

**conid:** int.  
 Contract ID of the requested contract.

**ticker:** String.  
 Ticker symbol of the requested contract.

**secType:** String.  
 Security type of the requested contract.

**listingExchange:** String.  
 Primary exchange of the requested contract.

**exchange:** String.  
 Traded exchange of the requested contract set in the request.

**companyName:** String.  
 Company name of the requested contract.

**currency:** String.  
 National currency of the requested contract.

**validExchanges:** String.  
 All valid exchanges of the requested contract.

**priceRendering:** String.  
 Render price of the requested contract.

**maturityDate:** String.  
 Maturity, or expiration date, of the requested contract.

**right:** String.  
 Right, put or call, of the requested contract.

**strike:** int.  
 Strike price of the requested contract.

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
  "category": "Computers"
}
```
