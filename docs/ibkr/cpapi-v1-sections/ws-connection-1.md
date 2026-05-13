### Request Session Information Copy Location

First make request the [/tickle](/campus/ibkr-api-page/cpapi-v1/#tickle) endpoint and save the returned session value.

```
{
    "session": "d21b8cf5ebc8ea01c6ce37c8125ec83f",
    "ssoExpires": ssoExpires,
    "collission": collission,
    "userId": userId,
    "hmds": {
        "error": "no bridge"
    },
    "iserver": {
        "authStatus": {
            "authenticated": true,
            "competing": false,
            "connected": true,
            "message": "",
            "MAC": "MAC",
            "serverInfo": {
                "serverName": "serverName",
                "serverVersion": "serverVersion"
            }
        }
    }
}
```
