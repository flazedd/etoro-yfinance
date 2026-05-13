### Order Status Copy Location

The Order Status endpoint may be used to monitor a single specific order while it remains active.

Important Notes:

- For multi-account structures such as Financial Advisors or linked-account structures, users must call [/iserver/account](/campus/ibkr-api-page/cpapi-v1/#switch-account) to switch to the affiliated account before requesting order status. It is otherwise expected to result in a ‘503’ error.
- If an order has been cancelled or filled prior to the active session and there is no cached information saved, querying the order status endpoint would be expected to result in a ‘503’ error.

Retrieve the given status of an individual order using the orderId returned by the order placement response or the orderId available in the live order response.

```
GET /iserver/account/order/status/{{ orderId }}
```

#### Request Object

###### Query Params

**orderId:** String. Required  
 Order identifier for the placed order. Returned by the order placement response or the orderId available in the live order response.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/account/order/status/1234567890"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/account/order/status/1234567890\
--request GET
```

#### Response Object

**sub\_type:** null.  
 Internal use only.

**request\_id:** String.  
 Returns the requestId of the order palced by the user.

**order\_id:** int.  
 Returns the orderId of the requested order.

**conidex:** String.  
 Returns the contract identifier for the order.

**conid:** int.  
 Returns the contract identifier for the order.

**symbol:** String.  
 Returns the ticker symbol for the order.

**side:** String.  
 Returns the side of the order.

**contract\_description\_1:** String.  
 Returns the local symbol of the order.

**listing\_exchange:** String.  
 Returns the primary listing exchange of the orer.

**option\_acct:** String.  
 For Client Portal use (Internal use only).

**company\_name:** String.  
 Returns the company long name.

**size:** String.  
 Returns the quantity of the order.

**total\_size:** String.  
 Returns the maximum quantity of the order.

**currency:** String.  
 Returns the base currency of the order.

**account:** String.  
 Returns the account the order was placed for.

**order\_type:** String.  
 Returns the order type for the given order.

**cum\_fill:** String.  
 Returns the cumulative fill of the order.

**order\_status:** String.  
 Returns the current status of the order.

**order\_ccp\_status:** String.  
 Returns the current status of the order as a code.

**order\_status\_description:** String.  
 Returns the human readable response of the order status.

**tif:** String.  
 Returns the time in force of the order.

**fg\_color:** String.  
 For Client Portal use (Internal use only).

**bg\_color:** String.  
 For Client Portal use (Internal use only).

**order\_not\_editable:** bool.  
 Returns whether or not the order can be modified.  
 This is relevant for orders that are currently or have already been executed.

**editable\_fields:** null.  
 For Client Portal use (Internal use only).

**cannot\_cancel\_order:** bool.  
 Returns whether or not the order can be cancelled.  
 This is relevant for orders that are currently or have already been executed.

**deactivate\_order:** bool.  
 Return whether or not the order has been marked inactive.

**sec\_type:** String.  
 Returns the security type of the order’s contract.

**available\_chart\_periods:** String.  
 For Client Portal use (Internal use only).

**order\_description:** String.  
 Returns the description of the order including the side, size, order type, price, and tif.

**order\_description\_with\_contract:** String.  
 Returns the description of the order including the side, size, symbol, order type, price, and tif.

**alert\_active:** int.  
 Returns wheteher or not there is an active alert available on the order.

**child\_order\_type:** String.  
 type of the child order  
 Value Format: A=attached, B=beta-hedge, 0=No Child

**order\_clearing\_account:** String.  
 Returns the accountID for the submitted order.

**size\_and\_fills:** String.  
 Returns the size of the order and how much of it has been filled.

**exit\_strategy\_display\_price:** String.  
 Displays the price of the order as it resolved its execution.

**exit\_strategy\_chart\_description:** String.  
 Returns the description of the order including the side, size, order type, price, and tif.

**average\_price:** String.  
 Returns the average price of execution for the order.

**exit\_strategy\_tool\_availability:** String.  
 Internal use only.

**allowed\_duplicate\_opposite:** bool.  
 Returns whether or not the opposing order can be placed on the market.

**order\_time:** String.  
 Returns the datetime of the order placement.  
 Time returned is based on UTC timezone.  
 Value Format: YYMMDDHHmmss

```
{
  "sub_type": null,
  "request_id": "209",
  "server_id": "0",
  "order_id": 1799796559,
  "conidex": "265598",
  "conid": 265598,
  "symbol": "AAPL",
  "side": "S",
  "contract_description_1": "AAPL",
  "listing_exchange": "NASDAQ.NMS",
  "option_acct": "c",
  "company_name": "APPLE INC",
  "size": "0.0",
  "total_size": "5.0",
  "currency": "USD",
  "account": "U1234567",
  "order_type": "MARKET",
  "cum_fill": "5.0",
  "order_status": "Filled",
  "order_ccp_status": "2",
  "order_status_description": "Order Filled",
  "tif": "DAY",
  "fg_color": "#FFFFFF",
  "bg_color": "#000000",
  "order_not_editable": true,
  "editable_fields":"",
  "cannot_cancel_order": true,
  "deactivate_order": false,
  "sec_type": "STK",
  "available_chart_periods": "#R|1",
  "order_description": "Sold 5 Market, Day",
  "order_description_with_contract": "Sold 5 AAPL Market, Day",
  "alert_active": 1,
  "child_order_type": "0",
  "order_clearing_account": "U1234567",
  "size_and_fills": "5",
  "exit_strategy_display_price": "193.12",
  "exit_strategy_chart_description": "Sold 5 @ 192.26",
  "average_price": "192.26",
  "exit_strategy_tool_availability": "1",
  "allowed_duplicate_opposite": true,
  "order_time": "231211180049"
}
```
