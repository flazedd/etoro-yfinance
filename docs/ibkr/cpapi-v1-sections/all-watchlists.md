### Get All Watchlists Copy Location

Retrieve a list of all available watchlists for the account.

`GET /iserver/watchlists`

#### Request Object:

###### Body Params

**SC:** String.  
 Specify the scope of the request.  
 Valid Values: USER\_WATCHLIST

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/watchlist?SC=USER_WATCHLIST"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/watchlists?SC=USER_WATCHLIST \
--request GET
```

#### Response Object

**data:** Object.  
 Contains all of the data about the watchlist.  
 {  
 **scanners\_only:** bool.  
 Shows if the system is only displaying scanners.

**system\_lists:** Array of Objects.  
 Returns all IB-created watchlists.  
 [{  
 **is\_open:** bool.  
 Internal use only.

**read\_only:** bool.  
 Returns if the watchlist can be edited or not.

**name:** String.  
 Returns the human-readable name of the watchlist.

**id:** String.  
 Returns the code identifier of the watchlist.

**type:** String.  
 Returns the watchlist type.  
 Always returns “watchlist”.  
 }],

**show\_scanners:** bool.  
 Returns if scanners are shown.

**bulk\_delete:** bool.  
 Displays if the watchlists should be deleted.

**user\_lists:** Array of Objects.  
 Returns all of the available user-created lists.  
 [{  
 **is\_open:** bool.  
 Internal use only.

**read\_only:** bool.  
 Returns if the watchlist can be edited or not.

**name:** String.  
 Returns the human-readable name of the watchlist.

**id:** String.  
 Returns the code identifier of the watchlist.

**type:** String.  
 Returns the watchlist type.  
 Always returns “watchlist”.  
 }]  
 },

**action:** String.  
 Internal use only.  
 Returns “content”.

**MID:** String.  
 Returns the number of times the endpoint was requested this session.  
 }

```
{
  "data": {
    "scanners_only": false,
    "show_scanners": false,
    "bulk_delete": false,
    "user_lists": [
      {
        "is_open": false,
        "read_only": false,
        "name": "Test Watchlist",
        "modified": 1702581306241,
        "id": "1234",
        "type": "watchlist"
      }
    ]
  },
  "action": "content",
  "MID": "1"
}
```
