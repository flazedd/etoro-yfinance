### Retrieve the Report Copy Location

Next, you’ll make a GET request to the `/GetStatement` endpoint, again passing your access token, but now passing the reference code obtained from the prior endpoint:

`https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/GetStatement?t={AccessToken}&q={ReferenceCode}&v=3`

Depending on the size of the request, you may need to wait longer between the /SendRequest and /GetStatement endpoint calls for the full report to finish generating.
