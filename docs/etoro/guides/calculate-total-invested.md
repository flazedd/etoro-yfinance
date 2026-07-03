> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Calculate Total Invested

> Learn how to calculate your total invested amount in demo or real accounts.

Total invested represents the total amount of capital you have allocated across all positions and pending orders. It is calculated by summing all position amounts, mirror position amounts, mirror available amounts (adjusted for closed positions), and pending order amounts.

<Note>
  Total invested only refers to your USD balance.
</Note>

To retrieve the data needed for this calculation, use the P\&L endpoint for either demo or real accounts.

## The Calculation Process

Calculating total invested involves fetching your account data and summing all amounts allocated to positions and orders.

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
Total Invested = Σ(positions[i].amount)
               + Σ(mirrors[i].positions[j].amount)
               + Σ(mirrors[i].availableAmount - mirrors[i].closedPositionsNetProfit)
               + Σ(ordersForOpen[i].amount where mirrorID = 0)
               + Σ(orders[i].amount)
               + Σ(ordersForOpen[i].totalExternalCosts where mirrorID = 0)
```

Where:

* `positions` is an array of your open positions
* `mirrors` is an array of your copy trading portfolios
* `mirrors[i].positions` is an array of positions within each mirror portfolio
* `mirrors[i].availableAmount` is the available amount in each mirror portfolio
* `mirrors[i].closedPositionsNetProfit` is the net profit from closed positions in each mirror portfolio
* `ordersForOpen` is an array of pending market orders (filtered to only include manual positions where `mirrorID = 0`)
* `orders` is an array of pending Market-if-touched orders
* `totalExternalCosts` is the total external costs for each order
* `amount` is the allocated amount for each position or order

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
          // Sum all position amounts
          const positionsAmount = data.positions.reduce((sum, pos) => sum + pos.amount, 0);
          
          // Sum all mirror position amounts and adjusted available amounts
          let mirrorsPositionsAmount = 0;
          let mirrorsAdjustedAmount = 0;
          data.mirrors.forEach(mirror => {
              mirrorsPositionsAmount += mirror.positions.reduce((sum, pos) => sum + pos.amount, 0);
              mirrorsAdjustedAmount += (mirror.availableAmount - mirror.closedPositionsNetProfit);
          });
          
          // Sum manual pending orders (mirrorID = 0)
          const ordersForOpenAmount = data.ordersForOpen
              .filter(order => order.mirrorID === 0)
              .reduce((sum, order) => sum + order.amount, 0);
          
          // Sum all orders
          const ordersAmount = data.orders.reduce((sum, order) => sum + order.amount, 0);
          
          // Sum external costs for manual pending orders
          const externalCosts = data.ordersForOpen
              .filter(order => order.mirrorID === 0)
              .reduce((sum, order) => sum + order.totalExternalCosts, 0);
          
          const totalInvested = positionsAmount + mirrorsPositionsAmount + mirrorsAdjustedAmount 
                              + ordersForOpenAmount + ordersAmount + externalCosts;
          
          console.log("Total Invested:", totalInvested);
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
      
      # Sum all position amounts
      positions_amount = sum(pos['amount'] for pos in data['positions'])
      
      # Sum all mirror position amounts and adjusted available amounts
      mirrors_positions_amount = sum(
          pos['amount'] 
          for mirror in data['mirrors'] 
          for pos in mirror['positions']
      )
      mirrors_adjusted_amount = sum(
          mirror['availableAmount'] - mirror['closedPositionsNetProfit']
          for mirror in data['mirrors']
      )
      
      # Sum manual pending orders (mirrorID = 0)
      orders_for_open_amount = sum(
          order['amount'] 
          for order in data['ordersForOpen'] 
          if order['mirrorID'] == 0
      )
      
      # Sum all orders
      orders_amount = sum(order['amount'] for order in data['orders'])
      
      # Sum external costs for manual pending orders
      external_costs = sum(
          order['totalExternalCosts'] 
          for order in data['ordersForOpen'] 
          if order['mirrorID'] == 0
      )
      
      total_invested = (positions_amount + mirrors_positions_amount + mirrors_adjusted_amount 
                       + orders_for_open_amount + orders_amount + external_costs)
      
      print(f"Total Invested: {total_invested}")
  else:
      print(f"Error: {response.status_code}")
  ```
</CodeGroup>

### Example Calculation

If your account has:

* `positions`: Two positions with `amount` values of 500 and 300
* `mirrors`: One mirror portfolio with:
  * Two positions with `amount` values of 200 and 150
  * `availableAmount`: 100
  * `closedPositionsNetProfit`: 50
* `ordersForOpen`: One manual pending order with `amount` of 200 and `totalExternalCosts` of 10 (where `mirrorID = 0`)
* `orders`: One existing order with `amount` value of 150

Then your total invested would be:

```
(500 + 300) + (200 + 150) + (100 - 50) + 200 + 150 + 10 = 1560
```

### Best Practices

1. **Monitor Your Investment:** Regularly check your total invested to understand your capital allocation across all positions and orders.
2. **Account for Mirror Portfolios:** Remember that mirror portfolios contribute to your total invested through both their positions and adjusted available amounts.
3. **Include External Costs:** Don't forget to include external costs from manual pending orders in your calculation.
4. **Use the Correct Environment:** Make sure to use the demo endpoint when testing and the real endpoint for live trading.
