### Session Authentication Copy Location

An authenticated brokerage session is necessary to access order information, place orders, financial advisor information, or receive market data via Client Portal API, and generally across all /iserver endpoints. Individual clients using Client Portal API are required to use the API Gateway in order to establish a secure brokerage session.

Interactive Brokers permits a single username to be signed in once at any given time. However, the Client Portal API permits users to log in without connecting to their brokerage session. This allows brokerage sessions to continue trading while non-brokerage sessions can perform certain actions such as requesting portfolio information without breaking existing trading sessions.
