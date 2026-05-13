### Delete a Watchlist Copy Location

Permanently delete a specific watchlist for all platforms.

`DELETE /iserver/watchlist`

#### Request Object

**id:** String. Required  
 Include the watchlist ID you wish to delete.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/watchlist?id=1234"
requests.delete(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/watchlist?id=1234 \
--request DELETE
```

#### Response Object

**Data:** Object.  
 Returns the data about the deleted watchlist.

**deleted:** String.  
 Returns the ID for the deleted watchlist.

**action:** String.  
 Always returns “context”.

**MID:** String.  
 Returns the id for the number of times /iserver/watchlist was called this session.

```
{
  "data": {
    "deleted": "1234"
  },
  "action": "context",
  "MID": "2"
}
```
