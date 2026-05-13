### Specific Account's Portfolio Information Copy Location

Account information related to account Id /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint.

`GET /portfolio/{accountId}/meta`

#### Request Object

###### Path Params

**accountId:** String. Required  
 Specify the AccountID to receive portfolio information for.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/U1234567/meta"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/U1234567/meta \
--request GET
```

#### Response Object

**id:** String  
 The account ID for which account should place the order.

**accountId:** String  
 The account ID for which account should place the order.

**accountVan:** String  
 The account alias for which account should place the order.

**accountTitle:** String  
 Title of the account

**displayName:** String  
 The account ID for which account should place the order.

**accountAlias:** String  
 User customizable account alias. Refer to Configure Account Alias for details.

**accountStatus:** int.  
 When the account was opened in unix time.

**currency:** String  
 Base currency of the account.

**type:** String  
 Account Type

**tradingType:** String  
 Account trading structure.

**businessType:** String.  
 Returns the organizational strcuture of the account.

**ibEntity:** String.  
 Returns the entity of Interactive Brokers the account is tied to.

**faClient:** bool.  
 If an account is a sub-account to a Financial Advisor.

**clearingStatus:** String  
 Status of the Account  
 Potential Values: O: Open; P or N: Pending; A: Abandoned; R: Rejected; C: Closed.

**covestor:** bool.  
 Is a Covestor Account

**noClientTrading:** bool.  
 Returns if the client account may trade.

**trackVirtualFXPortfolio:** bool.  
 Returns if the account is tracking Virtual FX or not.

**parent:** {

**mmc:** Array of Strings.  
 Returns the Money Manager Client Account.

**accountId:** String  
 Account Number for Money Manager Client

**isMParent:** bool.  
 Returns if this is a Multiplex Parent Account

**isMChild:** bool.  
 Returns if this is a Multiplex Child Account

**isMultiplex:** bool.  
 Is a Multiplex Account. These are account models with individual account being parent and managed account being child.

}  
 **desc:** String  
 Returns an account description.  
 Value Format: “accountId – accountAlias”  
 }]

```
{
  "id": "U1234567",
  "PrepaidCrypto-Z": false,
  "PrepaidCrypto-P": false,
  "brokerageAccess": false,
  "accountId": "U1234567",
  "accountVan": "U1234567",
  "accountTitle": "",
  "displayName": "U1234567",
  "accountAlias": null,
  "accountStatus": 1644814800000,
  "currency": "USD",
  "type": "DEMO",
  "tradingType": "PMRGN",
  "businessType": "IB_PROSERVE",
  "ibEntity": "IBLLC-US",
  "faclient": false,
  "clearingStatus": "O",
  "covestor": false,
  "noClientTrading": false,
  "trackVirtualFXPortfolio": true,
  "parent": {
    "mmc": [],
    "accountId": "",
    "isMParent": false,
    "isMChild": false,
    "isMultiplex": false
  },
  "desc": "U1234567"
}
```
