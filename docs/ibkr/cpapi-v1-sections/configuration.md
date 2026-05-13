### Client Portal Configuration Copy Location

Before using the Flex Web Service API to programmatically retrieve Flex Query reports, you’ll need to manually obtain some values from within **Client Portal**:

1. An access token to authenticate our requests
2. One or more query IDs corresponding to the reports you’d like to fetch

If you want to retrieve Flex Queries that you’ve already created, you’ll need to log into Client Portal with the username that created them, as these Flex Query report configurations are username-specific. Once we obtain these values, however, the use of the Flex Web Service API does not involve your IB credentials. Your username will only be involved in any subsequent management of the access token or reconfiguration of the report templates.

**Note:**these steps can only be completed by logging in to the Client Portal directly.
