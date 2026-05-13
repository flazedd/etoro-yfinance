### Receive Brokerage Accounts Copy Location

Returns a list of accounts the user has trading access to, their respective aliases and the currently selected account. Note this endpoint must be called before modifying an order or querying open orders.

`GET /iserver/accounts`

#### Request Object:

No parameters necessary.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/accounts" 
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/accounts \ 
--request GET
```

#### Response Object:

**accounts:** Array of Strings.  
 Returns an array of all accessible accountIds.

**acctProps:** Json Object.  
 Returns an json object for each accessible account’s properties.

**hasChildAccounts:** bool.  
 Returns whether or not child accounts exist for the account.

**supportsCashQty:** bool  
 Returns whether or not the account can use Cash Quantity for trading.

**supportsFractions:** bool.  
 Returns whether or not the account can submit fractional share orders.

**allowCustomerTime:** bool.  
 Returns whether or not the account must submit “manualOrderTime” with orders or not.  
 If true, manualOrderTime **must** be included.  
 If false, manualOrderTime **cannot** be included.

**aliases:** JSON Object.  
 Returns any available aliases for the account.

**allowFeatures:** JSON object  
 JSON of allowed features for the account.

**showGFIS:** bool.  
 Returns if the account can access market data.

**showEUCostReport:** bool.  
 Returns if the account can view the EU Cost Report

**allowFXConv:** bool.  
 Returns if the account can convert currencies.

**allowFinancialLens:** bool.  
 Returns if the account can access the financial lens.

**allowMTA:** bool.  
 Returns if the account can use mobile trading alerts.

**allowTypeAhead:** bool.  
 Returns if the account can use Type-Ahead support for Client Portal.

**allowEventTrading:** bool.  
 Returns if the account can use Event Trader.

**snapshotRefreshTimeout:** int.  
 Returns the snapshot refresh timeout window for new data.

**liteUser:** bool.  
 Returns if the account is an IBKR Lite user.

**showWebNews:** bool.  
 Returns if the account can use News feeds via the web.  
 research: bool.

**debugPnl:** bool.  
 Returns if the account can use the debugPnl endpoint.

**showTaxOpt:** bool.  
 Returns if the account can use the Tax Optimizer tool

**showImpactDashboard:** bool.  
 Returns if the account can view the Impact Dashboard.

**allowDynAccount:** bool.  
 Returns if the account can use dynamic account changes.

**allowCrypto:** bool.  
 Returns if the account can trade crypto currencies.

**allowedAssetTypes:** bool.  
 Returns a list of asset types the account can trade.

**chartPeriods:** Json Object.  
 Returns available trading times for all available security types.

**groups:** Array.  
 Returns an array of affiliated groups.

**profiles:** Array.  
 Returns an array of affiliated profiles.

**selectedAccount:** String.  
 Returns currently selected account. See [Switch Account](/campus/ibkr-api-page/cpapi-v1/#switch-account) for more details.

**serverInfo:** JSON Object.  
 Returns information about the IBKR session. Unrelated to Client Portal Gateway.

**sessionId:** String.  
 Returns current session ID.

**isFT:** bool.  
 Returns fractional trading access.

**isPaper:** bool.  
 Returns account type status.

```
{
  "accounts": [
    "U1234567"
  ],
  "acctProps": {
    "U1234567": {
      "hasChildAccounts": false,
      "supportsCashQty": true,
      "noFXConv": false,
      "isProp": false,
      "supportsFractions": true,
      "allowCustomerTime": false
    }
  },
  "aliases": {
    "U1234567": "U1234567"
  },
  "allowFeatures": {
    "showGFIS": true,
    "showEUCostReport": false,
    "allowEventContract": true,
    "allowFXConv": true,
    "allowFinancialLens": false,
    "allowMTA": true,
    "allowTypeAhead": true,
    "allowEventTrading": true,
    "snapshotRefreshTimeout": 30,
    "liteUser": false,
    "showWebNews": true,
    "research": true,
    "debugPnl": true,
    "showTaxOpt": true,
    "showImpactDashboard": true,
    "allowDynAccount": false,
    "allowCrypto": false,
    "allowedAssetTypes": "STK,CRYPTO"
  },
  "chartPeriods": {
    "STK": [
      "*"
    ],
    "CRYPTO": [
      "*"
    ]
  },
  "groups": [],
  "profiles": [],
  "selectedAccount": "U1234567",
  "serverInfo": {
    "serverName": "JifN17091",
    "serverVersion": "Build 10.25.0p, Dec 5, 2023 5:48:12 PM"
  },
  "sessionId": "1234a5b.12345678",
  "isFT": false,
  "isPaper": false
}
```
