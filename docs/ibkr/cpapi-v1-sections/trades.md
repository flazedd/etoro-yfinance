### Trades Copy Location

Returns a list of trades for the currently selected account for current day and six previous days. It is advised to call this endpoint once per session.

```
GET /iserver/account/trades
```

#### Request Object

###### Query Params

**days:** String.  
 Specify the number of days to receive executions for, up to a maximum of 7 days.  
 If unspecified, only the current day is returned.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/trades?days=3"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/account/trades?days=3 \
--request GET
```

#### Response Object.

**execution\_id:** String.  
 Returns the execution ID for the trade.

**symbol:** String.  
 Returns the underlying symbol.

**supports\_tax\_opt:** String.  
 Returns whether or not tax optimizer is supported for the order.

**side:** String.  
 Returns the side of the order, Buy or Sell.

**order\_description:** String.  
 Returns the description of the order including the side, size, symbol, order type, price, and tif.

**order\_ref:** String.  
 User defined string used to identify the order. Value is set using “cOID” field while placing an order.

**trade\_time:** String.  
 Returns the UTC format of the trade time.

**trade\_time\_r:** int.  
 Returns the epoch time of the trade.

**size:** float.  
 Returns the quantity of the order.

**price:** String.  
 Returns the price of trade execution.

**submitter:** String.  
 Returns the username that submitted the order.

**exchange:** String.  
 Returns the exchange the order was executed on.

**commission:** String.  
 Returns the cost of commission for the trade.

**net\_amount:** float.  
 Returns the total net cost of the order.

**account:** String.  
 Returns the account identifier.

**accountCode:** String.  
 Returns the account identifier.

**company\_name:** String.  
 Returns the long name of the contract’s company.

**contract\_description\_1:** String.  
 Returns the local symbol of the order.

**sec\_type:** String.  
 Returns the security type of the contract.

**listing\_exchange:** String.  
 Returns the primary listing exchange of the contract.

**conid:** int.  
 Returns the contract identifier of the order.

**conidEx:** String.  
 Returns the contract identifier of the order.

**clearing\_id:** String.  
 Returns the clearing firm identifier.

**clearing\_name:** String.  
 Returns the clearing firm identifier.

**liquidation\_trade:** String.  
 Returns whether the order was part of an account liquidation or note.

**is\_event\_trading:** String.  
 Returns whether the order was part of event trading or not.

```
[
  {
    "execution_id": "0000e0d5.6576fd38.01.01",
    "symbol": "AAPL",
    "supports_tax_opt": "1",
    "side": "S",
    "order_description": "Sold 5 @ 192.26 on ISLAND",
    "trade_time": "20231211-18:00:49",
    "trade_time_r": 1702317649000,
    "size": 5.0,
    "price": "192.26",
    "order_ref": "Order123",
    "submitter": "user1234",
    "exchange": "ISLAND",
    "commission": "1.01",
    "net_amount": 961.3,
    "account": "U1234567",
    "accountCode": "U1234567",
    "account_allocation_name": "U1234567",
    "company_name": "APPLE INC",
    "contract_description_1": "AAPL",
    "sec_type": "STK",
    "listing_exchange": "NASDAQ.NMS",
    "conid": 265598,
    "conidEx": "265598",
    "clearing_id": "IB",
    "clearing_name": "IB",
    "liquidation_trade": "0",
    "is_event_trading": "0"
  }
]
```
