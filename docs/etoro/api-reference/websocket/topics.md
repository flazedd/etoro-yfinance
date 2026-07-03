> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Topics

> Topics for the eToro WebSocket API

## Instrument Topics

Subscribe to real-time market price updates for various instruments.

### Request

```json theme={null}
{
    "id": "ed72693c-1545-4fa1-8a10-aca7cf5419a6",
    "operation": "Subscribe",
    "data": {
        "topics": ["instrument:<instrumentId>","instrument:<instrumentId>",...],
        "snapshot": <true / false>
    }
}
```

### Response

```json theme={null}
{
    "messages": [
        {
            "topic": "instrument:100000",
            "content": "{\"Ask\":\"84917.73\",\"Bid\":\"83232.21\",\"LastExecution\":\"84072.94\",\"Date\":\"2025-04-01T08:36:02.8305456Z\",\"NewUnitMargin\":\"83232.21\",\"UnitMarginAsk\":\"84917.73\",\"UnitMarginBid\":\"83232.21\",\"PriceRateID\":\"106439224591\",\"BidDiscounted\":\"84072.94\",\"AskDiscounted\":\"84076.96\",\"UnitMarginBidDiscounted\":\"84072.94\",\"UnitMarginAskDiscounted\":\"84076.96\"}",
            "id": "f1992278-2c4a-4b8f-92d6-8b99f5e1cb00",
            "type": "Trading.Instrument.Rate"
        }
    ]
}
```

### Prettified Content Field

```json theme={null}
{
    "Ask": "84917.73",
    "Bid": "83232.21",
    "LastExecution": "84072.94",
    "Date": "2025-04-01T08:36:02.8305456Z",
    "NewUnitMargin": "83232.21",
    "UnitMarginAsk": "84917.73",
    "UnitMarginBid": "83232.21",
    "PriceRateID": "106439224591",
    "BidDiscounted": "84072.94",
    "AskDiscounted": "84076.96",
    "UnitMarginBidDiscounted": "84072.94",
    "UnitMarginAskDiscounted": "84076.96"
}
```

### Rate Object Schema

<ResponseField name="Ask" type="number <float>">
  Current asking price (offer) for the instrument. This is the price at which you can buy the asset.
</ResponseField>

<ResponseField name="Bid" type="number <float>">
  Current bid price for the instrument. This is the price at which you can sell the asset.
</ResponseField>

<ResponseField name="LastExecution" type="number <float>">
  Price of the most recent trade execution for this instrument.
</ResponseField>

<ResponseField name="Date" type="string <date-time>">
  The date-time of the price in the system.
</ResponseField>

<ResponseField name="NewUnitMargin" type="number <float>" deprecated>
  USD equivalent of the instrument price.
</ResponseField>

<ResponseField name="UnitMarginAsk" type="number <float>" deprecated>
  USD equivalent of the instrument ask price.
</ResponseField>

<ResponseField name="UnitMarginBid" type="number <float>" deprecated>
  USD equivalent of the instrument bid price.
</ResponseField>

<ResponseField name="PriceRateID" type="integer">
  Unique identifier of the rate.
</ResponseField>

<ResponseField name="BidDiscounted" type="number <float>" deprecated>
  Obsolete.
</ResponseField>

<ResponseField name="AskDiscounted" type="number <float>" deprecated>
  Obsolete.
</ResponseField>

<ResponseField name="UnitMarginBidDiscounted" type="number <float>" deprecated>
  Obsolete.
</ResponseField>

<ResponseField name="UnitMarginAskDiscounted" type="number <float>" deprecated>
  Obsolete.
</ResponseField>

## Transaction Updates

Receive real-time updates on transactions and orders from your portfolio.

### Request

```json theme={null}
{
    "id": "ed72693c-1545-4fa1-8a10-aca7cf5419a6",
    "operation": "Subscribe",
    "data": {
        "topics": ["private"],
        "snapshot": <true / false>
    }
}
```

### Response

```json theme={null}
{
    "messages": [
        {
            "topic": "private",
            "content": "{\"OrderID\":981286176,\"OrderType\":20,\"CID\":32612044,\"StatusID\":11,\"InstrumentID\":1111,\"UnitsToDeduct\":0.0,\"RequestGuid\":\"fca38698-1fcf-407d-b930-3222e57274fa\",\"RequestOccurred\":\"2025-04-01T08:55:53.6910145Z\",\"RequestToken\":\"fca38698-1fcf-407d-b930-3222e57274fa\",\"ErrorCode\":0,\"RequestedUnits\":13.859902,\"ExecutedUnits\":0.0,\"EndRate\":0.0,\"NetProfit\":0.0,\"CloseReason\":0,\"PendingClosePositionIDs\":[2980225895],\"OpenDateTime\":\"2025-04-01T08:55:53.6910145Z\",\"IsInMirror\":false,\"StatusId\":11,\"TotalExternalFees\":0.0,\"TotalExternalTaxes\":0.0,\"LotsToDeduct\":0.0,\"RequestedLots\":13.859902,\"ExecutedLots\":0.0}",
            "id": "5263070a-c52f-436b-8ca8-10b3bd6d2970",
            "type": "Trading.OrderForCloseMultiple.Update"
        }
    ]
}
```

### Prettified Content Field

```json theme={null}
{
    "OrderID": 981286176,
    "OrderType": 20,
    "CID": 32613364,
    "StatusID": 11,
    "InstrumentID": 1111,
    "UnitsToDeduct": 0,
    "RequestGuid": "fca38698-1fcf-407d-b930-3222e57274fa",
    "RequestOccurred": "2025-04-01T08:55:53.6910145Z",
    "RequestToken": "fca38698-1fcf-407d-b930-3222e57274fa",
    "ErrorCode": 0,
    "RequestedUnits": 13.859902,
    "ExecutedUnits": 0,
    "EndRate": 0,
    "NetProfit": 0,
    "CloseReason": 0,
    "PendingClosePositionIDs": [
        2980225895
    ],
    "OpenDateTime": "2025-04-01T08:55:53.6910145Z",
    "IsInMirror": false,
    "StatusId": 11,
    "TotalExternalFees": 0,
    "TotalExternalTaxes": 0,
    "LotsToDeduct": 0,
    "RequestedLots": 13.859902,
    "ExecutedLots": 0
}
```
