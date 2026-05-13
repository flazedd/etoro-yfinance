### Using Flex Web Service Copy Location

The Flex Web Service API consists of two endpoints. Obtaining Flex Query reports via the Flex Web Service API is a two-step workflow involving requests to both endpoints in sequence. First, you will make a request to trigger IB’s backend to generate an instance of your report, which will populate your Flex Query template with the available data. In response, you’ll receive a reference code identifying this particular instance of the report. Next, you’ll make a request to fetch the generated report using the reference code.

Note that all requests must include a User-Agent header.
