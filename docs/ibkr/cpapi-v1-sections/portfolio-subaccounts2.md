### Portfolio Subaccounts (Large Account Structures) Copy Location

Used in tiered account structures (such as Financial Advisor and IBroker Accounts) to return a list of sub-accounts, paginated up to 20 accounts per page, for which the user can view position and account-related information. This endpoint must be called prior to calling other /portfolio endpoints for those sub-accounts. If you have less than 100 sub-accounts use /portfolio/subaccounts. To query a list of accounts the user can trade, see /iserver/accounts.

`GET /portfolio/subaccounts2`

#### Request Object

**page:** String. Required  
 Indicate the page identifier that should be retrieved.  
 Pagination begins at page 0.  
 20 accounts returned per page.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/subaccounts2?page=0"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/subaccounts2?page=0 \
--request GET
```

#### Response Object

**metadata:** Object.  
 Contains metadata about the response data.  
 {  
 **total:** int.  
 Displays the total number of accounts returned.

**pageSize:** int.  
 Returns the page size.

**pageNum:** int.  
 Returns the page number or identifier of the request.

**subaccounts:** Array of Objects.  
 Contains all of the accounts and their respective data.  
 [{  
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
[
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
]
```
