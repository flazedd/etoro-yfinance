### Order Submission Copy Location

Submission of orders for Event Contracts via the Web API functions like orders for any other instrument.

However, it is important to note the differing mechanics between CME Group products and ForecastEx instruments:

- CME Group instruments can be bought and sold and function as normal futures options.
- ForecastEx instruments cannot be sold, only bought. To exit or reduce a position, one must buy the opposing Event Contract, and IB will net the opposing positions together automatically.

In both cases, no short selling is permitted.
