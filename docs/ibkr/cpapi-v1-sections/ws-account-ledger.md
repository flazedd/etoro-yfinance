### Subscribe Account Ledger Copy Location

#### Subscribe to Account Ledger Topic

###### Topic:

**sld**  
 Subscribes to a stream of account ledger messages for the specified account, with contents sorted by currency.

###### Topic Target:

**accountId:** Required.  
 Must pass the account ID whose ledger data will be subscribed.

###### Parameters:

{  
 **keys:** Array of Strings.  
 Pass specific ledger currency keys to receive messages with data only for those currencies. Passing no named keys when opening the subscription will deliver ledger messages containing values for all currencies in the selected account.  
 Example Values: “LedgerListEUR”, “LedgerListUSD”, “LedgerListBASE” (for the account’s base currency)

**fields:** Array of Strings.  
 Pass specific ledger field names to receive messages only those data points for the currencies specified in the keys argument. Passing no named fields when opening the subscription will deliver all available data points for the specified currencies.  
 Example Values: “cashBalance”, “exchangeRate”  
 }

```
sld+DU1234567+{
    "keys":["LedgerListBASE","LedgerListEUR"],
    "fields":["cashBalance","exchangeRate"]
}
```

#### Account Ledger Topic Messages

A new message is published every 10 seconds until the sld topic is unsubscribed. A given message will only deliver a currency’s field data when a change occurred for that currency in the preceding interval. If no change occurred, the currency’s entry in the sld message will be “blank”, containing only the currency key and a timestamp.  
 Note that all currency values of JSON number type will be presented with a fractional component following a decimal point, and may also include an exponential component following an E if sufficiently large.

{  
 **result:** Array of JSON objects, with each object containing the set of key-value pairs for one currency in the account.  
   [  
     {  
 **key:** String.  
 Currency identifier string in the form “LedgerListXXX”, where XXX is the three-character currency code of a currency in the requested account, or “LedgerListBASE”, corresponding to the account’s base currency.  
 This is always returned.

**timestamp:** Number (integer only).  
 The timestamp reflecting when the currency’s set of values was retrieved.  
 This is always returned.

**acctCode:** String.  
 The account containing the currency position described by the accompanying data.

**cashbalance:** Number.  
 **cashBalanceFXSegment:** Number.  
 **commodityMarketValue:** Number.  
 **corporateBondsMarketValue:** Number.  
 **dividends:** Number.  
 **exchangeRate:** Number.  
 **funds:** Number.  
 **marketValue:** Number.  
 **optionMarketValue:** Number.  
 **interest:** Number.  
 **issueOptionsMarketValue:** Number.  
 **moneyFunds:** Number.  
 **netLiquidationValue:** Number.  
 **realizedPnl:** Number.  
 **unrealizedPnl:** Number.  
 **secondKey:** String.  
 **settledCash:** Number.  
 **stockMarketValue:** Number.  
 **tBillsMarketValue:** Number.  
 **tBondsMarketValue:** Number.  
 **warrantsMarketValue:** Number.

**severity:** Number (integer only).  
 Internal use only.  
     },  
     …  
   ]  
 }

```
{
  "result": [
    {
      "acctCode": "DU1234567",
      "cashbalance": 2.0201311791131118E8,
      "cashBalanceFXSegment": 0.0,
      "commodityMarketValue": 0.0,
      "corporateBondsMarketValue": 0.0,
      "key": "LedgerListBASE",
      "dividends": 0.0,
      "exchangeRate": 1.0,
      "funds": 0.0,
      "marketValue": 0.0,
      "optionMarketValue": 0.0,
      "interest": 396687.69214935537,
      "issueOptionsMarketValue": 0.0,
      "moneyFunds": 0.0,
      "netLiquidationValue": 2.0280151634374067E8,
      "realizedPnl": 0.0,
      "unrealizedPnl": 249013.5397937378,
      "secondKey": "BASE",
      "settledCash": 2.0201311791131118E8,
      "severity": 0,
      "stockMarketValue": 391710.74028015137,
      "tBillsMarketValue": 0.0,
      "tBondsMarketValue": 0.0,
      "warrantsMarketValue": 0.0,
      "timestamp": 1700248325
    },
    {
      "key": "LedgerListCAD",
      "timestamp": 1700248325
    },
    {
      "key": "LedgerListUSD",
      "timestamp": 1700248325
    },
    {
      "key": "LedgerListEUR",
      "timestamp": 1700248325
    },
    {
      "key": "LedgerListCHF",
      "timestamp": 1700248325
    }
  ],
  "topic": "sld+DU1234567"
}
```
