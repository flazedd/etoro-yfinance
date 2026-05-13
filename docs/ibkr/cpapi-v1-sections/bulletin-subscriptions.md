### Get a List of Subscriptions Copy Location

Return the current choices of subscriptions for notifications.

`GET /fyi/settings`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/fyi/settings"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/fyi/settings \
--request GET
```

#### Response Object

**A:** int.  
 Returns if the subscription can be modified.  
 Only returned if the subscription can be modified.  
 See /fyi/settings/{typecode} for how to modify.

**FC:** String.  
 Fyi code for enabling or disabling the notification.

**H:** int.  
 Disclaimer if the notification was read.  
 Value Format: 0: Unread; 1: Read

**FD:** String.  
 Returns a detailed description of the topic.

**FN:** String.  
 Returns a human readable title for the notification.

```
[
  {
    "FC": "M8",
    "H": 0,
    "A": 1,
    "FD": "Notify me when I establish position subject to US dividend tax withholding 871(m) rules.",
    "FN": "871(m) Trades"
  },
  {
    "FC": "AA",
    "H": 0,
    "A": 1,
    "FD": "Notifications related to account activity such as funding, application, trading and market data permission status",
    "FN": "Account Activity"
  },
  {...}
]
```
