> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Open and close market orders

> Learn how to programmatically execute trades to enter and exit positions using the eToro API.

Once you have resolved your target asset's `instrumentId`, you can begin executing trades. The eToro API separates trading logic into two distinct phases: opening a new position and closing an existing one.

## Opening a Position

Use the v2 order endpoint to open a market position. You can specify exactly one sizing field: `amount`, `units`, or `contracts`.

### Method 1: By Amount (Cash)

This is the most common method for dollar-cost averaging or fixed-budget strategies. You specify the cash value (e.g., \$1,000) and the API calculates the units based on the current market price.

**Endpoint:** `POST /api/v2/trading/execution/orders`

> **Note:** You can apply additional settings such as leverage, stop-loss, and take-profit during this request.

### Method 2: By Units (Volume)

Use this method when you need to control the exact volume of the asset (e.g., buying exactly 1.5 Bitcoin or 10 shares of Apple).

**Endpoint:** `POST /api/v2/trading/execution/orders`

### Example Request (Open by Amount)

The following examples demonstrate the full flow: **Search** for 'BTC' to get its ID, then **Buy** \$1,000 worth of it.

<CodeGroup>
  ```bash cURL theme={null}
  # 1. Search for the Instrument ID (Symbol: BTC)
  # Returns a JSON object containing the "InstrumentID" (e.g., 100000)
  curl -X GET "https://public-api.etoro.com/api/v1/market-data/search?internalSymbolFull=BTC" \
    -H "x-api-key: <YOUR_PUBLIC_KEY>" \
    -H "x-user-key: <YOUR_USER_KEY>" \
    -H "x-request-id: <UUID>"

  # 2. Use the ID from step 1 (e.g., 100000) to place the order
  curl -X POST "https://public-api.etoro.com/api/v2/trading/execution/orders" \
    -H "x-api-key: <YOUR_PUBLIC_KEY>" \
    -H "x-user-key: <YOUR_USER_KEY>" \
    -H "x-request-id: <UUID>" \
    -H "Content-Type: application/json" \
    -d '{
          "action": "open",
          "transaction": "buy",
          "symbol": "BTC",
          "instrumentId": 100000,
          "orderType": "mkt",
          "leverage": 1,
          "amount": 1000,
          "orderCurrency": "usd"
        }'
  ```

  ```javascript JavaScript theme={null}
  const crypto = require('crypto');

  const placeOrder = async () => {
    const symbol = 'BTC';
    const headers = {
      'x-api-key': '<YOUR_PUBLIC_KEY>',
      'x-user-key': '<YOUR_USER_KEY>',
      'x-request-id': crypto.randomUUID(), // or 'your-unique-uuid'
      'Content-Type': 'application/json'
    };

    try {
      // 1. Get Instrument ID
      const searchUrl = `https://public-api.etoro.com/api/v1/market-data/search?internalSymbolFull=${symbol}`;
      const searchRes = await fetch(searchUrl, { headers });
      const searchData = await searchRes.json();
      
      // Find exact match
      const instrument = searchData.items.find(i => i.internalSymbolFull === symbol);
      if (!instrument) throw new Error(`Instrument ${symbol} not found`);
      
      const instrumentId = instrument.instrumentId;
      console.log(`Resolved ${symbol} to ID: ${instrumentId}`);

      // 2. Place Order
      const orderUrl = 'https://public-api.etoro.com/api/v2/trading/execution/orders';
      const orderBody = {
        action: 'open',
        transaction: 'buy',
        symbol,
        instrumentId,
        orderType: 'mkt',
        leverage: 1,
        amount: 1000,
        orderCurrency: 'usd'
      };

      const orderRes = await fetch(orderUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(orderBody)
      });
      
      console.log("Order Response:", await orderRes.json());

    } catch (err) {
      console.error(err);
    }
  };

  placeOrder();
  ```

  ```python Python theme={null}
  import requests
  import uuid

  symbol = "BTC"
  headers = {
      "x-api-key": "<YOUR_PUBLIC_KEY>",
      "x-user-key": "<YOUR_USER_KEY>",
      "x-request-id": str(uuid.uuid4()),
      "Content-Type": "application/json"
  }

  # 1. Get Instrument ID
  search_url = "https://public-api.etoro.com/api/v1/market-data/search"
  search_res = requests.get(search_url, headers=headers, params={"internalSymbolFull": symbol})
  search_data = search_res.json()

  # Find exact match
  instrument = next((i for i in search_data['items'] if i['internalSymbolFull'] == symbol), None)

  if instrument:
      instrument_id = instrument['instrumentId']
      print(f"Resolved {symbol} to ID: {instrument_id}")

      # 2. Place Order
      order_url = "https://public-api.etoro.com/api/v2/trading/execution/orders"
      payload = {
          "action": "open",
          "transaction": "buy",
          "symbol": symbol,
          "instrumentId": instrument_id,
          "orderType": "mkt",
          "leverage": 1,
          "amount": 1000,
          "orderCurrency": "usd"
      }

      order_res = requests.post(order_url, json=payload, headers=headers)
      print("Order Response:", order_res.json())

  else:
      print(f"Instrument {symbol} not found")
  ```
</CodeGroup>

## Closing a Position

To close a trade, you must reference the specific `positionId` of the open position. You cannot simply "sell" the instrument; you must close the specific line item in your portfolio.

**Endpoint:** `POST /api/v1/trading/execution/market-close-orders/positions/{positionId}`

### Full vs. Partial Close

You can choose to close the entire position or just a portion of it.

* **Full Close:** Omit the `UnitsToDeduct` parameter or set it to `null`. This liquidates the entire position.
* **Partial Close:** Provide a specific value for `UnitsToDeduct`. Only that portion of the position will be closed, leaving the remainder active.

### Example Request (Close Position)

<CodeGroup>
  ```bash cURL theme={null}
  # Closing position ID 12345678
  curl -X POST "https://public-api.etoro.com/api/v1/trading/execution/market-close-orders/positions/12345678" \
    -H "x-api-key: <YOUR_PUBLIC_KEY>" \
    -H "x-user-key: <YOUR_USER_KEY>" \
    -H "x-request-id: <UUID>" \
    -H "Content-Type: application/json" \
    -d '{
          "InstrumentId": 100000,
          "UnitsToDeduct": null
        }'
  ```

  ```javascript JavaScript theme={null}
  const positionId = '12345678';
  const url = `https://public-api.etoro.com/api/v1/trading/execution/market-close-orders/positions/${positionId}`;

  fetch(url, {
    method: 'POST',
    headers: {
      'x-api-key': '<YOUR_PUBLIC_KEY>',
      'x-user-key': '<YOUR_USER_KEY>',
      'x-request-id': 'your-uuid-here',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      InstrumentId: 100000,
      UnitsToDeduct: null
    })
  })
  .then(res => res.json())
  .then(console.log)
  .catch(console.error);
  ```

  ```python Python theme={null}
  import requests
  import uuid

  position_id = "12345678"
  url = f"https://public-api.etoro.com/api/v1/trading/execution/market-close-orders/positions/{position_id}"
  headers = {
      "x-api-key": "<YOUR_PUBLIC_KEY>",
      "x-user-key": "<YOUR_USER_KEY>",
      "x-request-id": str(uuid.uuid4()),
      "Content-Type": "application/json"
  }

  payload = {
      "InstrumentId": 100000,
      "UnitsToDeduct": None
  }

  response = requests.post(url, json=payload, headers=headers)
  print(response.json())
  ```
</CodeGroup>

## Important Considerations

1. **Instrument IDs:** You must know the numeric `instrumentId` before placing an order. Use the Search endpoint to resolve tickers (e.g., AAPL) to IDs.
2. **Demo Environment:** When testing, use `POST /api/v2/trading/execution/demo/orders` to avoid risking real capital.
3. **Market Rates:** It is recommended to check current rates using `GET /api/v1/market-data/instruments/rates` before executing orders to ensure price accuracy.
