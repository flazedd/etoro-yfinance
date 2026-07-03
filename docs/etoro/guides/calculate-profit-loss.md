> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Calculate Profit/Loss

> Learn how to calculate your profit/loss (unrealized PnL) in demo or real accounts.

Profit/Loss represents your unrealized profit and loss across all open positions. It is calculated by summing the unrealized PnL from all your positions, mirror positions, and the net profit from closed positions in your mirror portfolios.

<Note>
  Profit/Loss appears as "Profit/Loss" in the app and represents your unrealized PnL.
</Note>

To retrieve the data needed for this calculation, use the P\&L endpoint for either demo or real accounts.

## The Calculation Process

Calculating profit/loss involves fetching your account data and summing all unrealized PnL values from positions and closed position profits.

### 1. Endpoints

Use the **P\&L** endpoint to retrieve your account information.

**Demo Account:** `GET https://public-api.etoro.com/api/v1/trading/info/demo/pnl`

**Real Account:** `GET https://public-api.etoro.com/api/v1/trading/info/real/pnl`

### 2. Header Requirements

Remember to include your authentication headers with every request.

* `x-api-key`
* `x-user-key`
* `x-request-id`

### 3. Calculation Formula

```
Profit/Loss = Σ(positions[i].unrealizedPnL.pnL)
            + Σ(mirrors[i].positions[j].unrealizedPnL.pnL)
            + Σ(mirrors[i].closedPositionsNetProfit)
```

Where:

* `positions` is an array of your open positions
* `positions[i].unrealizedPnL.pnL` is the unrealized profit/loss for each position
* `mirrors` is an array of your copy trading portfolios
* `mirrors[i].positions` is an array of positions within each mirror portfolio
* `mirrors[i].positions[j].unrealizedPnL.pnL` is the unrealized profit/loss for each mirror position
* `mirrors[i].closedPositionsNetProfit` is the net profit from closed positions in each mirror portfolio

## Examples

<CodeGroup>
  ```bash cURL theme={null}
  curl -X GET "https://public-api.etoro.com/api/v1/trading/info/demo/pnl" \
    -H "x-api-key: <YOUR_PUBLIC_KEY>" \
    -H "x-user-key: <YOUR_USER_KEY>" \
    -H "x-request-id: <UUID>"
  ```

  ```javascript JavaScript theme={null}
  const url = 'https://public-api.etoro.com/api/v1/trading/info/demo/pnl';

  fetch(url, options)
      .then(res => res.json())
      .then(data => {
          // Sum unrealized PnL from all positions
          const positionsPnL = data.positions.reduce((sum, pos) => sum + pos.unrealizedPnL.pnL, 0);
          
          // Sum unrealized PnL from mirror positions and closed positions net profit
          let mirrorsPnL = 0;
          let closedPositionsProfit = 0;
          data.mirrors.forEach(mirror => {
              mirrorsPnL += mirror.positions.reduce((sum, pos) => sum + pos.unrealizedPnL.pnL, 0);
              closedPositionsProfit += mirror.closedPositionsNetProfit;
          });
          
          const profitLoss = positionsPnL + mirrorsPnL + closedPositionsProfit;
          
          console.log("Profit/Loss:", profitLoss);
      })
      .catch(err => console.error(err));
  ```

  ```python Python theme={null}
  import requests
  import uuid

  url = "https://public-api.etoro.com/api/v1/trading/info/demo/pnl"

  headers = {
      "x-api-key": "<YOUR_PUBLIC_KEY>",
      "x-user-key": "<YOUR_USER_KEY>",
      "x-request-id": str(uuid.uuid4())
  }

  response = requests.get(url, headers=headers)

  if response.status_code == 200:
      data = response.json()
      
      # Sum unrealized PnL from all positions
      positions_pnl = sum(pos['unrealizedPnL']['pnL'] for pos in data['positions'])
      
      # Sum unrealized PnL from mirror positions
      mirrors_pnl = sum(
          pos['unrealizedPnL']['pnL']
          for mirror in data['mirrors']
          for pos in mirror['positions']
      )
      
      # Sum closed positions net profit
      closed_positions_profit = sum(
          mirror['closedPositionsNetProfit']
          for mirror in data['mirrors']
      )
      
      profit_loss = positions_pnl + mirrors_pnl + closed_positions_profit
      
      print(f"Profit/Loss: {profit_loss}")
  else:
      print(f"Error: {response.status_code}")
  ```
</CodeGroup>

### Example Calculation

If your account has:

* `positions`: Two positions with `unrealizedPnL.pnL` values of 50 and -20
* `mirrors`: One mirror portfolio with:
  * Two positions with `unrealizedPnL.pnL` values of 30 and 15
  * `closedPositionsNetProfit`: 100

Then your profit/loss would be:

```
(50 + (-20)) + (30 + 15) + 100 = 175
```

### Best Practices

1. **Monitor Regularly:** Check your profit/loss frequently to track the performance of your open positions.
2. **Understand Components:** Remember that profit/loss includes both unrealized PnL from open positions and realized profits from closed mirror positions.
3. **Consider Market Volatility:** Unrealized PnL can fluctuate with market conditions, so monitor it alongside your total invested amount.
4. **Use the Correct Environment:** Make sure to use the demo endpoint when testing and the real endpoint for live trading.
