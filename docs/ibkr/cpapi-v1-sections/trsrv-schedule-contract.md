### Trading Schedule by Symbol Copy Location

Returns the trading schedule up to a month for the requested contract

`GET /trsrv/secdef/schedule`

#### Request Object

###### Query Params

**assetClass:** *String.* Required  
 Specify the security type of the given contract.  
 Value Formats: Stock: STK, Option: OPT, Future: FUT, Contract For Difference: CFD, Warrant: WAR, Forex: SWP, Mutual Fund: FND, Bond: BND, Inter-Commodity Spreads: ICS

**conid:** *String.* Required  
 Provide the contract identifier to retrieve the trading schedule for.

**symbol:** *String.* Required  
 Specify the symbol for your contract.

**exchange:** *String.*  
 Specify the primary exchange of your contract.

**exchangeFilter:** *String.*  
 Specify exchange you want to retrieve data from.

- Python
- cURL

```
request_url = f"{baseUrl}/trsrv/secdef//schedule?assetClass=STK&conid=265598&symbol=AAPL&exchange=ISLAND&exchangeFilter=ISLAND"
requests.get(url=requests_url)
```

```
curl \
--url {{baseUrl}}/secdef/trsrv/schedule?assetClass=STK&symbol=AAPL&exchange=ISLAND&exchangeFilter=ISLAND,NYSE,AMEX \
--request GET
```

#### Response Object

**id:** String.  
 Exchange parameter id

**tradeVenueId:** String.  
 Reference on a trade venue of given exchange parameter

**schedules:** Array of Objets.  
 Always contains at least one ‘tradingTime’ and zero or more ‘sessionTime’ tags

**clearingCycleEndTime:** int.  
 End of clearing cycle.

**tradingScheduleDate:** int.  
 Date of the clearing schedule.  
 20000101 stands for any Sat, 20000102 stands for any Sun, … 20000107 stands for any Fri. Any other date stands for itself.

**sessions:** Object.  
 description: String.  
 If the LIQUID hours differs from the total trading day then a separate ‘session’ tag is returned.

**openingTime:** int.  
 Opening date time of the session.

**closingTime:** int.  
 Closing date time of the sesion.

**prop:** String.  
 If the whole trading day is considered LIQUID then the value ‘LIQUID’ is returned.

**tradingTimes:** Object.  
 Object containing trading times.

**description:** String  
 Returns tradingTime in exchange time zone.

**openingTime:** int.  
 Opening time of the trading day.

**closingTime:** int.  
 Closing time of the trading day.

**cancelDayOrders:** string.  
 Cancel time for day orders.

```
[
  {
    "id": "p102082",
    "tradeVenueId": "v13133",
    "timezone": "America/New_York",
    "schedules": [      
      {
        "clearingCycleEndTime": "2000",
        "tradingScheduleDate": "20000103",
        "sessions": [
          {
            "openingTime": "0930",
            "closingTime": "1600",
            "prop": "LIQUID"
          }
        ],
        "tradingtimes": [
          {
            "openingTime": "0400",
            "closingTime": "2000",
            "cancelDayOrders": "Y"
          }
        ]
      },
      {...}
    ]
  }
]
```
