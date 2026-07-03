> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Calculate Equity

> Learn how to calculate your equity in demo or real accounts.

Equity represents the total value of your account, including your available cash, invested capital, and unrealized profit/loss. It is calculated by summing your available cash, total invested amount, and unrealized PnL.

<Note>
  Equity only refers to your USD balance.
</Note>

To retrieve the data needed for this calculation, use the P\&L endpoint for either demo or real accounts.

## The Calculation Process

Calculating equity involves fetching your account data and combining three key components: available cash, total invested, and unrealized PnL.

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

```text theme={null}
Equity = Available Cash + Total Invested + Unrealized PnL
```

Where:

* **Available Cash** = `credit - (Σ(ordersForOpen[i].amount where mirrorID = 0) + Σ(orders[i].amount))`
* **Total Invested** = `Σ(positions[i].amount) + Σ(mirrors[i].positions[j].amount) + Σ(mirrors[i].availableAmount - mirrors[i].closedPositionsNetProfit) + Σ(ordersForOpen[i].amount where mirrorID = 0) + Σ(orders[i].amount) + Σ(ordersForOpen[i].totalExternalCosts where mirrorID = 0)`
* **Unrealized PnL** = `Σ(positions[i].unrealizedPnL.pnL) + Σ(mirrors[i].positions[j].unrealizedPnL.pnL) + Σ(mirrors[i].closedPositionsNetProfit)`

<Info>
  For detailed information on calculating each component, see:

  * [Calculate Available Cash](/guides/calculate-available-cash)
  * [Calculate Total Invested](/guides/calculate-total-invested)
  * [Calculate Profit/Loss](/guides/calculate-profit-loss)
</Info>

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
          // Calculate Available Cash
          const credits = data.credits;
          const ordersForOpenAmount = data.ordersForOpen
              .filter(order => order.mirrorID === 0)
              .reduce((sum, order) => sum + order.amount, 0);
          const ordersAmount = data.orders.reduce((sum, order) => sum + order.amount, 0);
          const availableCash = credits - (ordersForOpenAmount + ordersAmount);
          
          // Calculate Total Invested
          const positionsAmount = data.positions.reduce((sum, pos) => sum + pos.amount, 0);
          let mirrorsPositionsAmount = 0;
          let mirrorsAdjustedAmount = 0;
          data.mirrors.forEach(mirror => {
              mirrorsPositionsAmount += mirror.positions.reduce((sum, pos) => sum + pos.amount, 0);
              mirrorsAdjustedAmount += (mirror.availableAmount - mirror.closedPositionsNetProfit);
          });
          const externalCosts = data.ordersForOpen
              .filter(order => order.mirrorID === 0)
              .reduce((sum, order) => sum + order.totalExternalCosts, 0);
          const totalInvested = positionsAmount + mirrorsPositionsAmount + mirrorsAdjustedAmount 
                              + ordersForOpenAmount + ordersAmount + externalCosts;
          
          // Calculate Unrealized PnL
          const positionsPnL = data.positions.reduce((sum, pos) => sum + pos.unrealizedPnL.pnL, 0);
          let mirrorsPnL = 0;
          let closedPositionsProfit = 0;
          data.mirrors.forEach(mirror => {
              mirrorsPnL += mirror.positions.reduce((sum, pos) => sum + pos.unrealizedPnL.pnL, 0);
              closedPositionsProfit += mirror.closedPositionsNetProfit;
          });
          const unrealizedPnL = positionsPnL + mirrorsPnL + closedPositionsProfit;
          
          // Calculate Equity
          const equity = availableCash + totalInvested + unrealizedPnL;
          
          console.log("Equity:", equity);
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
      
      # Calculate Available Cash
      credits = data['credits']
      orders_for_open_amount = sum(order['amount'] for order in data['ordersForOpen'] if order['mirrorID'] == 0)
      orders_amount = sum(order['amount'] for order in data['orders'])
      available_cash = credits - (orders_for_open_amount + orders_amount)
      
      # Calculate Total Invested
      positions_amount = sum(pos['amount'] for pos in data['positions'])
      mirrors_positions_amount = sum(
          pos['amount'] 
          for mirror in data['mirrors'] 
          for pos in mirror['positions']
      )
      mirrors_adjusted_amount = sum(
          mirror['availableAmount'] - mirror['closedPositionsNetProfit']
          for mirror in data['mirrors']
      )
      external_costs = sum(
          order['totalExternalCosts'] 
          for order in data['ordersForOpen'] 
          if order['mirrorID'] == 0
      )
      total_invested = (positions_amount + mirrors_positions_amount + mirrors_adjusted_amount 
                       + orders_for_open_amount + orders_amount + external_costs)
      
      # Calculate Unrealized PnL
      positions_pnl = sum(pos['unrealizedPnL']['pnL'] for pos in data['positions'])
      mirrors_pnl = sum(
          pos['unrealizedPnL']['pnL']
          for mirror in data['mirrors']
          for pos in mirror['positions']
      )
      closed_positions_profit = sum(
          mirror['closedPositionsNetProfit']
          for mirror in data['mirrors']
      )
      unrealized_pnl = positions_pnl + mirrors_pnl + closed_positions_profit
      
      # Calculate Equity
      equity = available_cash + total_invested + unrealized_pnl
      
      print(f"Equity: {equity}")
  else:
      print(f"Error: {response.status_code}")
  ```
</CodeGroup>

### Example Calculation

If your account has:

* **Available Cash**: 450
* **Total Invested**: 1560
* **Unrealized PnL**: 175

Then your equity would be:

```text theme={null}
450 + 1560 + 175 = 2185
```

### Best Practices

1. **Monitor Total Account Value:** Equity gives you a complete picture of your account's total value, including both liquid and invested capital.
2. **Track Performance:** Compare your equity over time to understand your overall trading performance.
3. **Risk Management:** Use equity to calculate position sizes and manage risk appropriately.
4. **Use the Correct Environment:** Make sure to use the demo endpoint when testing and the real endpoint for live trading.
