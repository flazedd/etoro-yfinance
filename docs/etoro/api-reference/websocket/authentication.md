> ## Documentation Index
> Fetch the complete documentation index at: https://api-portal.etoro.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Authentication

> Authentication of the eToro WebSocket API

To use certain WebSocket channels, you must authenticate with your User and API keys.

### Request

```json theme={null}
{
    "id": "ed72693c-1545-4fa1-8a10-aca7cf5419a6",
    "data": {
        "userKey": "<your user key>",
        "apiKey": "<your API key>"
    }
}
```

### Successful Response

```json theme={null}
{
    "id": "ed72693c-1545-4fa1-8a10-aca7cf5419a6",
    "success": true,
    "operation": "Authenticate"
}
```

### Unsuccessful Response

```json theme={null}
{
    "id": "ed72693c-1545-4fa1-8a10-aca7cf5419a6",
    "success": false,
    "operation": "Authenticate",
    "errorMessage": "<Error Message>",
    "errorCode": "<Error Code>"
}
```

### Error Codes

<ResponseField name="SessionAlreadyAuthenticated" type="Error Code">
  Session is already authenticated
</ResponseField>

<ResponseField name="DataRequired" type="Error Code">
  Data is required
</ResponseField>

<ResponseField name="ApiKeyRequired" type="Error Code">
  ApiKey is required
</ResponseField>

<ResponseField name="UserKeyRequired" type="Error Code">
  UserKey is required
</ResponseField>

<ResponseField name="TooManyRequests" type="Error Code">
  Too many requests
</ResponseField>

<ResponseField name="Forbidden" type="Error Code">
  Access to this resource is forbidden. Please contact customer support for assistance
</ResponseField>

<ResponseField name="UnhandledException" type="Error Code">
  Global Error
</ResponseField>

<ResponseField name="InvalidKey" type="Error Code">
  Key is invalid
</ResponseField>

<ResponseField name="Unauthorized" type="Error Code">
  Unauthorized
</ResponseField>
