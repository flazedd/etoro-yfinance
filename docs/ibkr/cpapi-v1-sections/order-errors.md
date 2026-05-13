### Order Error Details Copy Location

The WebAPI contains an array of unique error response systems dependent upon the layer a request fails at. The table below describes the status code, status message, and error message that may have lead to the issue.

#### Web API Errors

| Status Code | Status Message | Error Message | Context |
| --- | --- | --- | --- |
| 400 | BadRequest | Failed to parse body as JSON. Content Type: application/json; charset=utf-8 | Request body is not properly formatted as JSON. |
| 400 | BadRequest | orders request includes parameter with incorrect type | Field requiring a specific variable type is receiving an invalid type. See Place Order reference for support types. |
| 400 | BadRequest | Invalid Side (must be ‘BUY’ or ‘SELL’). | Value for Side is invalid. |
| 400 | BadRequest | Unknown order type | Provided order type is inaccurate. |
| 400 | BadRequest | conid or conidex is required | conid or conidex are not included or misspelled. |

#### Interactive Brokers Errors & Precautions

| Status Code | Status Message | Error Message | Context |
| --- | --- | --- | --- |
| 200 | OK | Invalid order price fields | Price value is not supported. Ensure the price adheres to market rules. |
| 200 | OK | null time in force is not supported for this order | No tif value was given, or the tif value was invalid. |
| 200 | OK | “id”:”{{Reply\_ID}}”,”message”:[“{{Message}}”],”isSuppressed”:false,”messageIds”:[“{{Message\_ID}}”],”messageOptions”:[“Yes”,”No”] | See [Suppressible Message IDs](/campus/ibkr-api-page/cpapi-v1/#suppressible-id) for specific ID information. |
| 200 | OK | no sec defs returned forSecDef reqId=resolve ecReqByConid13297 | Provided conid or conidex is invalid. Verify contract against /iserver/secdef/info. |
