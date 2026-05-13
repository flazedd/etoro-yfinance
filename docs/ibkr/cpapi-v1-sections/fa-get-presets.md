### Retrieve Allocation Presets Copy Location

Retrieve the preset behavior for allocation groups for specific events.

`GET /iserver/account/allocation/presets`

#### Request Object

No params or body content should be sent.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/marketdata/unsubscribeall"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/account/allocation/presets \
--request GET
```

#### Response Object

group\_auto\_close\_positions: bool.

default\_method\_for\_all: String.

profiles\_auto\_close\_positions: bool.

strict\_credit\_check: bool.

group\_proportional\_allocation: bool.

```
{
  "group_auto_close_positions": false,
  "default_method_for_all": "N",
  "profiles_auto_close_positions": false,
  "strict_credit_check": false,
  "group_proportional_allocation": false
}
```
