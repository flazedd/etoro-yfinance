> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Overview

> Overview of the eToro WebSocket API

### What is the WebSocket API

The eToro WebSocket API provides real-time streaming access to market data and trading events through a persistent connection. This API enables developers to build responsive applications that react instantly to market changes, order updates, and portfolio events without the overhead of constant HTTP polling.

The API uses JSON message format over WebSocket protocol, supporting both public market data streams and private authenticated feeds for personalized trading information.

### Key Features

* **Real-time Market Data:** Live price feeds for instruments with bid/ask prices

* **Trading Notifications:** Instant updates for order executions, position changes, and portfolio events

* **Flexible Subscriptions:** Subscribe to specific instruments or private data feeds based on your needs

* **Snapshot Support:** Optional initial snapshots when subscribing to topics for current state

* **Authentication Integration:** Secure access to private data using your eToro API credentials
