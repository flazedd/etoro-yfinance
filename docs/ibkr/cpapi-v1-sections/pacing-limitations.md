## Pacing Limitations Copy Location

Interactive Brokers has implemented pacing limits on endpoints accessible via Client Portal API.

- There is a global limit of 10 total requests per second.
- Some endpoint specific limits are also in place. These limits can be found in the table below.
- Any endpoint not listed in the table below follows the global restriction of 10 requests per second.

Where this limit is exceeded, the API will return a “429 Too Many Requests” exception. Violator IP addresses are put in a penalty box for 15 minutes. After this period, the IP address is removed from the penalty box until another request exceeds the limit again. Repeat violator IP addresses can be permanently blocked until the issue is resolved.

| Endpoint | Method | Limit |
| --- | --- | --- |
| /fyi/unreadnumber | GET | 1 req/sec |
| /fyi/settings | GET | 1 req/sec |
| /fyi/settings/{typecode} | POST | 1 req/sec |
| /fyi/disclaimer/{typecode} | GET | 1 req/sec |
| /fyi/disclaimer/{typecode} | PUT | 1 req/sec |
| /fyi/deliveryoptions | GET | 1 req/sec |
| /fyi/deliveryoptions/email | PUT | 1 req/sec |
| /fyi/deliveryoptions/device | POST | 1 req/sec |
| /fyi/deliveryoptions/{deviceId} | DELETE | 1 req/sec |
| /fyi/notifications | GET | 1 req/sec |
| /fyi/notifications/more | GET | 1 req/sec |
| /fyi/notifications/{notificationId} | PUT | 1 req/sec |
| /iserver/account/orders | GET | 1 req/5 secs |
| /iserver/account/pnl/partitioned | GET | 1 req/5 secs |
| /iserver/account/trades | GET | 1 req/5 secs |
| /iserver/marketdata/history | GET | 5 concurrent requests |
| /iserver/marketdata/snapshot | GET | 10 req/s |
| /iserver/scanner/params | GET | 1 req/15 mins |
| /iserver/scanner/run | POST | 1 req/sec |
| /pa/performance | POST | 1 req/15 mins |
| /pa/summary | POST | 1 req/15 mins |
| /pa/transactions | POST | 1 req/15 mins |
| /portfolio/accounts | GET | 1 req/5 secs |
| /portfolio/subaccounts | GET | 1 req/5 secs |
| /sso/validate | GET | 1 req/min |
| /tickle | GET | 1 req/sec |
