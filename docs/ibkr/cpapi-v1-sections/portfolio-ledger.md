### Portfolio Ledger Copy Location

Information regarding settled cash, cash balances, etc. in the account’s base currency and any other cash balances hold in other currencies. /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint. The list of supported currencies is available at https://www.interactivebrokers.com/en/index.php?f=3185.

`GET /portfolio/{accountId}/ledger`

#### Request Object

###### Path Params

**accountId:** String. Required  
 Specify the account ID for which account you require ledger information on.

- Python
- cURL

```
request_url = f"{baseUrl}/portfolio/U1234567/ledger"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/portfolio/U1234567/ledger \
--request GET
```

#### Response Object

**{currency}:** Object.  
 Returns the ledger values for the specified currency.  
 May return “BASE” to show your base currency.  
 {  
 **commoditymarketvalue:** float.  
 Returns the total market value of commodity positions in the given currency.

**futuremarketvalue:** float.  
 Returns the total market value of futures positions in the given currency.

**settledcash:** float.  
 Returns the total settled cash for the given currency.

**exchangerate:** int.  
 Returns the exchange rate from the base currency to the specified currency.

**sessionid:** int.  
 Internal use only.

**cashbalance:** float.  
 Returns the total cash available for trading in the given currency.

**corporatebondsmarketvalue:** float.  
 Returns the total market value of corporate bond positions in the given currency.

**warrantsmarketvalue:** float.  
 Returns the total market value of warrant positions in the given currency.

**netliquidationvalue:** float.  
 Returns the current net liquidation value of the positions held in the given currency.

**interest:** float.  
 Returns the margin interest rate on the given currency.

**unrealizedpnl:** float.  
 Returns the unrealized profit and loss for positions in the given currency.

**stockmarketvalue:** float.  
 Returns the total market value of stock positions in the given currency.

**moneyfunds:** float.  
 Returns the total market value of money funds positions in the given currency.

**currency:** String.  
 Returns the currency’s symbol.

**realizedpnl:** float.  
 Returns the realized profit and loss for positions in the given currency.

**funds:** float.  
 Returns the total market value of all funds positions in the given currency.

**acctcode:** String.  
 Returns the account ID for the account owner specified.

**issueroptionsmarketvalue:** float.  
 Returns the total market value of all issuer option positions in the given currency.

**key:** String.  
 Returns “LedgerList”. Internal use only.

**timestamp:** int.  
 Returns the timestamp for the value retrieved in epoch time.

**severity:** int.  
 Internal use only.

**stockoptionmarketvalue:** float.  
 Returns the total market value of all stock option positions in the given currency.

**futuresonlypnl:** float.

**tbondsmarketvalue:** float.  
 Returns the total market value of all treasury bond positions in the given currency.

**futureoptionmarketvalue:** float.  
 Returns the total market value of all futures option positions in the given currency.

**cashbalancefxsegment:** float.  
 Internal use only.

**secondkey:** String.  
 Returns the currency’s symbol.

**tbillsmarketvalue:** float.  
 Returns the total market value of all treasury bill positions in the given currency.

**dividends:** float.  
 Returns the value of dividends held from the given currency.  
 }

```
{
  "USD": {
    "commoditymarketvalue": 0.0,
    "futuremarketvalue": -1051.0,
    "settledcash": 214716688.0,
    "exchangerate": 1,
    "sessionid": 1,
    "cashbalance": 214716688.0,
    "corporatebondsmarketvalue": 0.0,
    "warrantsmarketvalue": 0.0,
    "netliquidationvalue": 215335840.0,
    "interest": 305569.94,
    "unrealizedpnl": 39695.82,
    "stockmarketvalue": 314123.88,
    "moneyfunds": 0.0,
    "currency": "USD",
    "realizedpnl": 0.0,
    "funds": 0.0,
    "acctcode": "U1234567",
    "issueroptionsmarketvalue": 0.0,
    "key": "LedgerList",
    "timestamp": 1702582321,
    "severity": 0,
    "stockoptionmarketvalue": -2.88,
    "futuresonlypnl": -1051.0,
    "tbondsmarketvalue": 0.0,
    "futureoptionmarketvalue": 0.0,
    "cashbalancefxsegment": 0.0,
    "secondkey": "USD",
    "tbillsmarketvalue": 0.0,
    "endofbundle": 1,
    "dividends": 0.0
  },
  "BASE": {
    "commoditymarketvalue": 0.0,
    "futuremarketvalue": -1051.0,
    "settledcash": 215100080.0,
    "exchangerate": 1,
    "sessionid": 1,
    "cashbalance": 215100080.0,
    "corporatebondsmarketvalue": 0.0,
    "warrantsmarketvalue": 0.0,
    "netliquidationvalue": 215721776.0,
    "interest": 305866.88,
    "unrealizedpnl": 39907.37,
    "stockmarketvalue": 316365.38,
    "moneyfunds": 0.0,
    "currency": "BASE",
    "realizedpnl": 0.0,
    "funds": 0.0,
    "acctcode": "U1234567",
    "issueroptionsmarketvalue": 0.0,
    "key": "LedgerList",
    "timestamp": 1702582321,
    "severity": 0,
    "stockoptionmarketvalue": -2.88,
    "futuresonlypnl": -1051.0,
    "tbondsmarketvalue": 0.0,
    "futureoptionmarketvalue": 0.0,
    "cashbalancefxsegment": 0.0,
    "secondkey": "BASE",
    "tbillsmarketvalue": 0.0,
    "dividends": 0.0
  }
}
```
