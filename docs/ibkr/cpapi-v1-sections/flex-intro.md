## Flex Web Service Copy Location

The Flex Web Service is a small, standalone HTTP API for programmatically generating and retrieving pre-configured Flex Queries. Flex Queries are first constructed manually as templates in Client Portal, after which the Flex Web Service API is used to generate an instance of a report populated with up-to-date data and deliver it back to the requesting client. The Flex Web Service offers access to the same Flex Query reports that you’d otherwise retrieve manually from within Client Portal.

For more information about Flex Queries and about IB’s reporting functionality overall, please consult the following documentation:

- [Flex Queries](https://www.ibkrguides.com/clientportal/performanceandstatements/flex.htm)
- [Reporting Guide](https://www.ibkrguides.com/clientportal/performanceandstatements/reports.htm)

**Usage Notes:**

1. Though Flex Query reports can be generated and retrieve at any time, the data they contain will not necessarily change throughout the day. “Activity Statement” Flex Queries contain data that is only updated once daily at close of business, so there is no benefit to generating and retrieving these reports more than once per day. Normally one would retrieve the prior day’s Activity Statements at the start of the following day, which guarantees that all values have been updated by IB’s reporting backend.
2. “Trade Confirmation” Flex Queries will yield updated data throughout the day as executions occur against working orders, but these execution entries are also not available in Trade Confirmation Flex Queries in real-time. Typically a new execution will be available for inclusion in a newly generated Flex Query report within 5 to 10 minutes.
3. Given the above restrictions on the refresh rate of Flex Query data, the Flex Web Service is not suitable for active polling for newly generated reports. Rather, it is best used to capture the desired reports once daily, or at most intermittently throughout the day in the case of Trade Confirmation reports.
4. Depending on the size of the report to be generated, there may be a slight delay between the initial request to generate the report and the report’s availability via the second request. Time to availability is also dependent on system utilization, so please permit some flexibility in the timing of the final report retrieval, either via an explicit “wait” between the first and second requests, or via periodic reattempts of the second request.
5. Note that the same Flex Query reports (as well as many other report types) can also be scheduled for delivery via email or FTP:
   - [Scheduled Delivery of User-Defined Flex Queries](https://www.ibkrguides.com/clientportal/performanceandstatements/deliverysettingsflex.htm)
   - [Scheduled Delivery of IB-Defined Statements](https://www.ibkrguides.com/clientportal/performanceandstatements/deliver.htm)
6. Flex queries using a variable duration, such as “Last N Days” will always use the maximum possible days for a given request, rather than following the last used number of days in Client Portal. It is recommended to use the precise request values such as “Last Month”, “Last Quarter”, “Year To Date”, etc.
