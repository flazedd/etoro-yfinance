> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Example code

> Example code for the eToro WebSocket API

Here is an example of how to connect to the WebSocket API using JavaScript:

```javascript theme={null}
let ws;
ws = new WebSocket("wss://ws.etoro.com/ws");

ws.onmessage = (event) => {
    // Implement your own logic here to handle incoming messages.
    logMessage("Received: " + event.data);
};

// Authenticate
const authRequest = {
    id: "<random guid>",
    operation: "Authenticate",
    data: {
        userKey: "<your user key>",
        apiKey: "<your API key>"
    }
};

ws.send(JSON.stringify(authRequest));

// Subscribe
const subscribeRequest = {
    id: "<random guid>",
    operation: "Subscribe",
    data: {
        topics: ["instrument:100000"], // Sending topic as an array
        snapshot: false
    }
};

ws.send(JSON.stringify(subscribeRequest));

// Unsubscribe
const unsubscribeRequest = {
    id: "<random guid>", 
    operation: "Unsubscribe",
    data: {
        topics: [topic] // Sending topic as an array
    }
};

ws.send(JSON.stringify(unsubscribeRequest));

// Close websocket
if (ws) {
    ws.close();
}
```
