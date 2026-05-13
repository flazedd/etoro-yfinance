### Search Bond Filter Information Copy Location

Request a list of filters relating to a given Bond issuerID. The issuerId is retrieved from [/iserver/secdef/search](/campus/ibkr-api-page/cpapi-v1/#search-symbol-contract) and can be used in [/iserver/secdef/info?issuerId={{ issuerId }}](/campus/ibkr-api-page/cpapi-v1/#secdef-info-contract) for retrieving conIds.

`/iserver/secdef/bond-filters`

#### Request Object

###### Query Params

**symbol:** String. Required  
 This should always be set to “BOND”

**issuerId:** String. Required  
 Specifies the issuerId value used to designate the bond issuer type.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/secdef/bond-filters?symbol=BOND&issuerId=e1400715"
requests.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/iserver/secdef/bond-filters?symbol=BOND&issuerId=e1400715 \
--request GET
```

**bondFilters:** Array of Objects.  
 Contains all filters pertaining to the given issuerId.  
 [{  
 **displayText:** String.  
 An identifier used to document returned options/values. This can be thought of as a key value.

**columnId:** int.  
 Used for user interfaces. Internal use only.

**options:** Array of objects.  
 Contains all objects with values corresponding to the parent displayText key.  
 [{  
 **text:** String.  
 In some instances, a text value will be returned, which indicates the standardized value format such as plaintext dates, rather than solely numerical values.

**value:** String.  
 Returns value directly correlating to the displayText key. This may include exchange, maturity date, issue date, coupon, or currency.

}]

}]

```
{
  "bondFilters": [
    {
      "displayText": "Exchange",
      "columnId": 0,
      "options": [
      {
        "value": "SMART"
      }]
    },
    {
      "displayText": "Maturity Date",
      "columnId": 27,
      "options": [
        {
          "text": "Jan 2025",
          "value": "202501"
      }]
    },
    {
      "displayText": "Issue Date",
      "columnId": 28,
      "options": [{
        "text": "Sep 18 2014",
        "value": "20140918"
      }]
    },
    {
      "displayText": "Coupon",
      "columnId": 25,
      "options": [{
        "value": "1.301"
      }]
    },
    {
      "displayText": "Currency",
      "columnId": 5,
      "options": [{
        "value": "EUR"
      }]
    }
  ]
}
```
