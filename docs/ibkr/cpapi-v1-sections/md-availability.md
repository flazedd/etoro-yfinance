### Market Data Availability Copy Location

The field may contain three chars.

First character defines market data timeline. This includes:  R = RealTime, D = Delayed, Z = Frozen, Y = Frozen Delayed, N = Not Subscribed.

Second character defines the data structure. This includes: P = Snapshot, p = Consolidated.

Third character defines the type of data: This will always return: B = Book

| Code | Name | Description |
| --- | --- | --- |
| R | RealTime | Data is relayed back in real time without delay, market data subscription(s) are required. |
| D | Delayed | Data is relayed back 15-20 min delayed. |
| Z | Frozen | Last recorded data at market close, relayed back in real time. |
| Y | Frozen Delayed | Last recorded data at market close, relayed back delayed. |
| N | Not Subscribed | User does not have the required market data subscription(s) to relay back either real time or delayed data. |
| O | Incomplete Market Data API Acknowledgement | The annual Market Data API Acknowledgement has not been completed for the given user. To complete the agreement:  1. Log in to the 2. Select “Welcome” in the top right corner, and then “Settings” 3. You will find a large button for “Market Data Subscriptions” on the right. 4. Find the “Market Data API Agreement” on the right. |
| P | Snapshot | Snapshot request is available for contract. |
| p | Consolidated | Market data is aggregated across multiple exchanges or venues. |
| B | Book | Top of the book data is available for contract. |
| d | Performance Details Enabled | Additional performance details are available for this contract. Internal use intended. |
