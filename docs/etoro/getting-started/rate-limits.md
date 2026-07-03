> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Rate Limits

> Understand the rate limits applied to the eToro Public API to ensure smooth and reliable integration.

To ensure platform stability and fair usage across all applications, the eToro Public API enforces rate limits on its endpoints. Limits are tracked per user key and are measured over a 1-minute rolling window.

If you exceed these limits, the API will return a `429 Too Many Requests` status code. We recommend implementing standard retry logic with exponential backoff to handle these gracefully.

## Standard Rate Limits

Rate limits generally fall into two categories depending on the performance impact of the request: standard data retrieval (Read) and transactional/heavy operations (Write & Execution).

### 60 Requests per Minute

Most standard `GET` requests for retrieving data allow up to **60 requests per minute**. This includes:

* **Market Data**: Retrieving instrument rates, historical candles, search, and exchanges.
* **Portfolio & Account Info**: Fetching Real and Demo portfolio details, PnL, and general user info.
* **Social & Feeds (Read)**: Reading user feeds, instrument feeds, curated lists, and market recommendations.
* **Watchlists (Read)**: Retrieving public, private, and default watchlists.

### 20 Requests per Minute

Endpoints that execute trades, modify state, or run heavier queries are limited to **20 requests per minute**. This includes:

* **Trading Execution**: Opening, closing, or canceling orders in both Real and Demo environments (`POST` and `DELETE` requests).
* **Watchlist Management**: Creating, updating, or deleting watchlists and their items (`POST`, `PUT`, `DELETE` requests).
* **Social & Feeds (Write)**: Creating new feed posts or posting reactions/comments (`POST` requests).
* **User Trade Info**: Fetching detailed historical trade info for a specific user profile.

<Note>
  **Best Practice**: Whenever possible, cache non-volatile data locally (such as Instrument IDs or basic Exchange data) to minimize unnecessary API calls and preserve your rate limit quota for real-time operations like trade execution.
</Note>
