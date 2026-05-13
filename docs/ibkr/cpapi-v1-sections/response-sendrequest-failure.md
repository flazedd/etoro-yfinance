### Failure response from /SendRequest Copy Location

**Status**. A failed request will deliver a Status of `Fail`.

**ErrorCode**.  
 A numeric code indicating the nature of the failure. See [Error Codes](#error-codes) for a list of error code values and their descriptions.

**ErrorMessage**.  
 A human-readable description of the error. See [Error Codes](#error-codes) for a list of error code values and their descriptions.

```
<FlexStatementResponse timestamp="28 August, 2012 10:37 AM EDT">
    <Status>Fail</Status>
    <ErrorCode>1012</ErrorCode>
    <ErrorMessage>Token has expired.</ErrorMessage>
</FlexStatementResponse>
```
