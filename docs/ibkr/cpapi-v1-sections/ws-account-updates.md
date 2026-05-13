### Account Updates Copy Location

Returns details about the brokerage accounts that the currently logged in user has access to. An initial message is sent when the user a connection to the websocket is first established, with supplemental messages are sent whenever there is a change to the account details.

**topic:** String.  
 Returns the topic of the given request.

**args:** Object.  
 Returns the object containing the pnl data.

**accounts:** Array.  
 Displays all accounts currently accessible by the user.

**acctProps:** Object.  
 Returns an object detailing the account properties.

**acctId:** Object.  
 Returns the specific allocation group or account information.

**hasChildAccounts:** bool.  
 Returns whether there are any subaccounts attached to the listed account.

**supportsCashQty:**bool.  
 Returns where the account supports cash quantity orders.

**noFXConv:** bool.  
 Returns if the account supports forex conversion.

**isProp:** bool.

**supportsFractions:** bool.  
 Returns if the account supports fractional trading.

**allowCustomerTime:** bool.  
 Returns if the account returns data in the customer’s local time.

**aliases:** Object.  
 Returns a series of accounts and their affiliated aliases.

**allowFeatures:**  Object.  
 Displays the allowed features for the account.

**showGFIS:** bool.  
 Determines whether the account can display data or not.

**showEUCostReport:** bool.  
 Determines if the account receives the EU Cost Report.

**allowEventContract:** bool.  
 Determines if the account can receive event contracts.

**allowFXConv:** bool.  
 Determines if the account allows forex conversions.

**allowFinancialLens:** bool.  
 Determines if the account supports Financial Lens (Client Portal Only).

**allowMTA:** bool.  
 Determines if the account supports Mobile Trading Alerts.

**allowTypeAhead:** bool.  
 Determines if the account supports Type Ahead (Client Portal Only).

**allowEventTrading:** bool.  
 Determines if the account supports Event Trader (Client Portal Only).

**snapshotRefreshTimeout:** int.  
 Determines if the account can support snapshot refresh (Client Portal Only).

**liteUser:** bool.  
 Returns if the account is an IBKR Lite account.

**showWebNews:** bool.  
 Returns if the account

**research:** bool.  
 Determines if the account supports research subscriptions.

**debugPnl:** bool.  
 Determines if the account enables debug for PnL (Client Portal Only).

**showTaxOpt:** bool.  
 Determines if the account supports Tax Optimizer (Client Portal Only).

**showImpactDashboard:** bool.  
 Determines if the account should display the Impact Dashboard on startup (Client Portal Only).

**allowDynAccount:** bool.  
 Determines if the account supports Dynamic Account Structures (Client Portal Only).

**allowCrypto:** bool.  
 Determines if the account supports Crypto trading.

**allowedAssetTypes:** String.  
 Returns all support asset or security types.

**chartPeriods:** Object of Arrays.  
 Returns the trading hours supported by each approvided asset type.

**groups:** Array.  
 Lists all groups the account is listed under.

**profiles:** Array.  
 Lists all profiles the account is listed under.

**selectedAccount:** String.  
 Returns the acively selected account.

**serverInfo:** Object.  
 Returns a description of the server info.

**sessionId:** String.  
 Returns the sesion identifier.

**isFT:** bool.  
 Returns if the fractional trading account.

**isPaper:** bool.  
 Returns if the active account is a paper trading account.

```
{
    "topic":"act",
    "args":{
       "accounts":[],
       "acctProps":{
          "All":{
             "hasChildAccounts":hasChildAccounts,
             "supportsCashQty":supportsCashQty,
             "noFXConv":noFXConv,
             "isProp":isProp,
             "supportsFractions":supportsFractions,
             "allowCustomerTime":allowCustomerTime
          }
       },
       "aliases":{},
       "allowFeatures":{
          "showGFIS":showGFIS,
          "showEUCostReport":showEUCostReport,
          "allowEventContract":allowEventContract,
          "allowFXConv":allowFXConv,
          "allowFinancialLens":allowFinancialLens,
          "allowMTA":allowMTA,
          "allowTypeAhead":allowTypeAhead,
          "allowEventTrading":allowEventTrading,
          "snapshotRefreshTimeout":snapshotRefreshTimeout,
          "liteUser":liteUser,
          "showWebNews":showWebNews,
          "research":research,
          "debugPnl":debugPnl,
          "showTaxOpt":showTaxOpt,
          "showImpactDashboard":showImpactDashboard,
          "allowDynAccount":allowDynAccount,
          "allowCrypto":allowCrypto,
          "allowedAssetTypes":"allowedAssetTypes"
       },
       "chartPeriods":{
          "STK":[],
          "CFD":[],
          "OPT":[],
          "FOP":[],
          "WAR":[],
          "IOPT":[],
          "FUT":[],
          "CASH":[],
          "IND":[],
          "BOND":[],
          "FUND":[],
          "CMDTY":[],
          "PHYSS":[],
          "CRYPTO":[]
       },
       "groups":[],
       "profiles":[],
       "selectedAccount":"selectedAccount",
       "serverInfo":{
          "serverName":"serverName",
          "serverVersion":"serverVersion"
       },
       "sessionId":"sessionId",
       "isFT":isFT,
       "isPaper":isPaper
    }
 }
```
