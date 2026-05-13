### Market Data Update Frequency Copy Location

Watchlist market data at Interactive Brokers is derived from time-based snapshot intervals which vary by product and region. This means that a given tick will only update as frequently as its interval allows. See the table for more details on product specifics.

Please keep in mind that the Web API still retains a standard pacing limit of 10 requests per second. For more frequency returns, implement the [smd websocket topic](/campus/ibkr-api-page/cpapi-v1/#ws-sub-watchlist-data) in place of the HTML endpoint.

| Product | Frequency |
| --- | --- |
| All Products | 500ms |
