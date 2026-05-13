### Overnight Order Submission Copy Location

Trading with the WebAPI allows users to submit orders in the [OVERNIGHT market](/en/trading/us-overnight-trading.php) using both OVERNIGHT exclusive orders as well as OVERNIGHT+DAY orders. This is handled by submitting the affiliated Time-In-Force value when [Placing an Order](/campus/ibkr-api-page/cpapi-v1/#place-order).

#### Overnight

Overnight orders are submitted using the “OVT” time in force value.

```
{ "tif": "OVT" }
```

#### Overnight+DAY

Overnight+DAY orders are submitted using the “OND” time in force value.

```
{ "tif": "OND" }
```
