### Transaction History Copy Location

Transaction history for a given number of conids and accounts.  
 Types of transactions include dividend payments, buy and sell transactions, transfers.

`POST /pa/transactions`

#### Request Object

###### Body Parameters

**acctIds:** Array of Strings. Required  
 Include each account ID to receive data for.

**conids:** Array of integers. Required  
 Include contract ID to receive data for.  
 Only supports one contract id at a time.

**currency:** String. Required  
 Define the currency to display price amounts with.  
 Defaults to USD.

**days:** String. Optional  
 Specify the number of days to receive transaction data for.  
 Defaults to 90 days of transaction history if unspecified.

- Python
- cURL

```
request_url = f"{baseUrl}/pa/transactions"
json_content = {
  "acctIds": [
    "U1234567"
  ],
  "conids": [
    265598
  ],
  "currency": "USD",
  "days": 3
}
requests.post(url=request_url, json=json_content)
```

```
curl \
--url {{baseUrl}}/pa/transactions\
--request POST \
--header 'Content-Type:application/json' \
--data '{
  "acctIds": [
    "U1234567"
  ],
  "conids": [
    265598
  ],
  "currency": "USD",
  "days": 3
}'
```

#### Response Object

**rc:** int.  
 (Client portal use only)

**nd:** int.  
 (Client portal use only)

**rpnl:** Object.  
 Rturns the object containing the realized pnl for the contract on the date.

**data:** Array of objects.  
 Returns an array of realized pnl objects.

**date:** String.  
 Specifies the date for the transaction.

**cur:** String.  
 Specifies the currency of the realized value.

**fxRate:** int.  
 Returns the foreign exchnage rate.

**side:** String.  
 Determines if the day was a loss or gain  
 Value format: “L”, “G”

**acctid:** String.  
 Returns the account ID the trade transacted on.

**amt:** String.  
 Returns the amount gained or lost on the day.

**conid:** String.  
 Returns the contract ID of the transaction.

**amt:** String.  
 Provides the total amount gained or lost from all days returned

**currency:** String.  
 Returns the currency the account is traded in.

**from:** int.  
 Returns the epoch time for the start of requests.

**id:** String.  
 Returns the request identifier, getTransactions.

**to:** int.  
 Returns the epoch time for the end of requests.

**includesRealTime:** bool.  
 Returns if the trades are up to date or not.

**transactions:** Array of objects.  
 Lists all supported transaction values.

**date:** String.  
 Reutrns the human-readable datetime of the transaction.  
 Value Format: “{Day of the week} {3-digit month} {day of the month} 00:00:00 {timezone} {year}”

**cur:** String.  
 Returns the currency of the traded insturment.

**fxRate:** int.  
 Returns the forex conversion rate.

**pr:** float.  
 Returns the price per share of the transaction.

**qty:** int.  
 Returns the total quantity traded.  
 Will display a negative value for sell orders, and a positive value for buy orders.

**acctid:** String.  
 Returns the account which made the transaction.

**amt:** float.  
 Returns the total value of the trade.

**conid:** int.  
 Returns the contract identifier.

**type:** String.  
 Returns the order side.

**desc:** String.  
 Returns the long name for the company.

```
{
  "rc": 0,
  "nd": 4,
  "rpnl": {
    "data": [
      {
        "date": "20231211",
        "cur": "USD",
        "fxRate": 1,
        "side": "L",
        "acctid": "U1234567",
        "amt": "12.2516",
        "conid": "265598"
      }
    ],
    "amt": "12.2516"
  },
  "currency": "USD",
  "from": 1702270800000,
  "id": "getTransactions",
  "to": 1702530000000,
  "includesRealTime": true,
  "transactions": [
    {
      "date": "Mon Dec 11 00:00:00 EST 2023",
      "cur": "USD",
      "fxRate": 1,
      "pr": 192.26,
      "qty": -5,
      "acctid": "U1234567",
      "amt": 961.3,
      "conid": 265598,
      "type": "Sell",
      "desc": "Apple Inc"
    }
  ]
}
```
