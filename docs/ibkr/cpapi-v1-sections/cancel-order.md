### Cancel Order Copy Location

Cancels an open order.

Must call /iserver/accounts endpoint prior to cancelling an order.

Use /iservers/account/orders endpoint to review open-order(s) and get latest order status.

`DELETE /iserver/account/{{ accountId }}/order/{{ orderId }}`

#### Request Object

###### Path Param

**accountId:** String.  
 The account ID for which account should place the order.

**orderId:** String.  
 The orderID for that should be modified.  
 Can be retrieved from /iserver/account/orders  
 Submitting ‘-1’ will cancel all open orders

###### Query Param

**manualIndicator:** Boolean. Required\*  
 **IMPORTANT** This field is required when trading Futures and Futures Options contracts to remain in compliance with [CME Group Rule 536-B](https://www.cmegroup.com/rulebook/files/cme-group-Rule-536-B-Tag1028.pdf).  
 The Manual Order Indicator is used to determine if an order was manually entered or handled through an automated tool. Regardless of original submission, the cancellation must also include the manualIndicator tag to signify of the order cancellation was done manually or autonomously.  
 true indicates the order was cancellation manually through an interface while false indicates an order was cancellation through an automated system.

**extOperator:** string. Required\*  
 **IMPORTANT** This field is required when trading Futures and Futures Options contracts to remain in compliance with [CME Group Rule 536-B](https://www.cmegroup.com/rulebook/files/cme-group-Rule-536-B-Tag1028.pdf).  
 The External Operator field should contain information regarding the submitting user in charge of the API operation at the time of request submission.

- Python
- cURL

request\_url = f”{baseUrl}/iserver/account/U1234567/order/123456789?manualIndicator=true&extOperator=person1234″  
 requests.delete(url=request\_url)

```
curl \
--url {{baseUrl}}/iserver/account/U1234567/order/123456789?manualIndicator=true&extOperator=person1234 \
--request DELETE
```

#### Response Object

**msg:** String.  
 Returns the confirmation of the request being submitted.

**order\_id:** int.  
 Returns the orderID of the cancelled order.

**conid:** int.  
 Returns the conid for the requested order to be cancelled.  
 Returns -1 for orders that were immediately cancelled on request.

**account:** String.  
 Returns the accountId for the requested order to be cancelled.  
 Returns null for orders that were immediately cancelled on request.

```
{
    "msg": "Request was submitted",
    "order_id": 123456789,
    "conid": 265598,
    "account": "U1234567"
}
```

#### Error Object

**error:** String.  
 Returns the error message.

```
{
    "error": "OrderID 1 doesn't exist"
}
```
