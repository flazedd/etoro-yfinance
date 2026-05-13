### Subscribing to Websocket Topics Copy Location

Most data available via the websocket is delivered as a stream of messages in response to an explicit subscription to a topic. Such subscription messages are solicited, because the client must first ask to be subscribed to the relevant topic before messages will be sent by the server. To subscribe to a topic, a message is sent to the websocket in the following format:

**TOPIC+[TOPIC\_TARGET]+{PARAMETERS}**

where:

- **TOPIC** is the identifier of the topic (the type of data) to be subscribed.
- The plus symbol **+** is used as a separator of the message elements.
- **TOPIC\_TARGET** identifies a specific resource, typically an account or instrument, as the subject of the subscription. Certain topics do not use a target.- **{PARAMETERS}** is a JSON-formatted string that describes filters or other modifiers to the topic subscription. If no parameters are available for the topic, or none are desired for your subscription, this is sent as an empty {} object.

Solicited message topics are generally three characters in length. A message sent to subscribe, as well as the messages received in response for the duration of the subscription, will use a topic starting with **s** (“subscribe”). The second two characters identify the particular datafeed in question, as in topic **ssd**, indicating “subscribe” + “account summary”.

When canceling a subscription (unsubscribing), a message is sent using a topic starting with **u** (“unsubscribe”), followed by the two-character identifier of the datafeed whose subscription will be terminated, as in topic **usd**, indicating “unsubscribe” + “account summary”. A single response message will be delivered with the same unsubscribe topic, confirming unsubscription.
