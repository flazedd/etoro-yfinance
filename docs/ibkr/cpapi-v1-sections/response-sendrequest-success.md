### Success response from /SendRequest Copy Location

**Status**. A value of `Success` indicates a successful request to generate the report. If the request failed, Status will deliver `Fail`.

**ReferenceCode**. If the request was successful, the XML response will contain this numeric reference code. This code will be used in the subsequent request to retrieve the generated Flex Query.

**url**. This is a legacy URL. Should be ignored.

```
<FlexStatementResponse timestamp="28 August, 2012 10:37 AM EDT">
    <Status>Success</Status>
    <ReferenceCode>1234567890</ReferenceCode>
   <url>https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement</url>
</FlexStatementResponse>
```
