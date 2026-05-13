## Websockets Copy Location

Websocket topics expose the same underlying data as is delivered by the HTTP endpoints. Functionality that requires a brokerage session (that is, all features behind /iserver URIs) will also require a brokerage session when accessed via websocket. Please ensure you have an active brokerage session before attempting to use these features of the websocket. For information on getting started with Client Portal API, please refer to the [Authentication](/campus/ibkr-api-page/cpapi-v1/#authentication) section.

Websocket topics requiring a brokerage session: smd (live market data), smh (historical market data), sbd (live price ladder data), sor (order updates), str (trades), act (unsolicited account property info), sts (unsolicited brokerage session authentication status), blt (unsolicited bulletins), ntf (unsolicited notifications).

Websocket topics that do not require a brokerage session: spl (profit & loss updates), ssd (account summary updates), sld (account ledger updates), system (unsolicited connection-related messages).

The url for websockets is: **wss://localhost:5000/v1/api/ws**
