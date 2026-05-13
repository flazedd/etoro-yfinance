### Search Contract by Symbol Copy Location

Search by underlying symbol or company name. Relays back what derivative contract(s) it has. This endpoint must be called before using /secdef/info.

For bonds, enter the family type in the symbol field to receive the issuerID used in the /iserver/secdef/info endpoint.

`GET /iserver/secdef/search`

#### Request Object

###### Query Params

**symbol:** String. Required  
 Underlying symbol of interest. May also pass company name if ‘name’ is set to true, or bond issuer type to retrieve bonds.

**name:** bool.  
 Determines if symbol reflects company name or ticker symbol. If company name is included will only receive limited response: conid, companyName, companyHeader and symbol. The inclusion of the name field will prohibit the [/iserver/secdef/strikes](/campus/ibkr-api-page/cpapi-v1/#strike-conid-contract) endpoint from returning data. After retrieving your expected contract, customers looking to create option chains should remove the name field from the request.

**secType:** String.  
 Valid Values: “STK”, “IND”, “BOND”  
 Declares underlying security type.

- Python
- cURL

```
request_url = f"{baseUrl}/iserver/secdef/search?symbol=Interactive Brokers&name=true"
requests.get(url=request_url)
```

```
curl --insecure \
--url https://localhost:5000/v1/api/iserver/secdef/search?symbol=Interactive Brokers&name=true \
--request GET
```

#### Response Object

**“conid”:** String.  
 Conid of the given contract.

**“companyHeader”:** String.  
 Extended company name and primary exchange.

**“companyName”:** String.  
 Name of the company.

**“symbol”:** String.  
 Company ticker symbol.

**“description”:** String.  
 Primary exchange of the contract.

**“restricted”:** bool.  
 Returns if the contract is available for trading.

**“sections”:** Array of objects

**“secType”:** String.  
 Given contracts security type.

**“months”:** String.  
 Returns a string of dates, separated by semicolons.  
 Value Format: “JANYY;FEBYY;MARYY”

**“symbol”:** String.  
 Symbol of the instrument.

**“exchange”:** String.  
 Returns a string of exchanges, separated by semicolons.  
 Value Format: “EXCH;EXCH;EXCH”

Unique for Bonds  
 **“issuers”:** Array of objects  
 Array of objects containing the id and name for each bond issuer.

**“id”:** String.  
 Issuer Id for the given contract.

**“name”:** String.  
 Name of the issuer.

**“bondid”:** int.  
 Bond type identifier.

**“conid”:** String.  
 Contract ID for the given bond.

**“companyHeader”:** String.  
 Name of the bond type  
 Value Format: “Corporate Fixed Income”

**“companyName”:** null  
 Returns ‘null’ for bond contracts.

**“symbol”:null**  
 Returns ‘null’ for bond contracts.

**“description”:null**  
 Returns ‘null’ for bond contracts.

**“restricted”:null**  
 Returns ‘null’ for bond contracts.

**“fop”:null**  
 Returns ‘null’ for bond contracts.

**“opt”:null**  
 Returns ‘null’ for bond contracts.

**“war”:null**  
 Returns ‘null’ for bond contracts.

**“sections”:** Array of objects  
 Only relays “secType”:”BOND” in the Bonds section.

```
[
  {
    "conid": "43645865",
    "companyHeader": "IBKR INTERACTIVE BROKERS GRO-CL A (NASDAQ) ",
    "companyName": "INTERACTIVE BROKERS GRO-CL A (NASDAQ)",
    "symbol": "IBKR",
    "description": null,
    "restricted": null,
    "sections": [],
    "secType": "STK"
  }
]
```
