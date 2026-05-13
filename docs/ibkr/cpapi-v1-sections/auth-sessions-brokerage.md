### Understanding Brokerage Sessions Copy Location

All resources behind /iserver are accessible only with an active “brokerage” session. Some additional info:

1. TWS being a trading platform requires that a username has trading permissions in order for it to be used to access TWS – there is no purely “read-only” TWS access
2. The Client Portal website, on the other hand, contains all of the reporting and account management functionality, and consequently it is possible to log in to Client Portal with a read-only/no-trading-permissions username and access reports, portfolio info, etc.
3. Iserver is effectively TWS running on IB infrastructure, and it serves all of the trading-permissions-required resources, hence the need for a brokerage session to access those endpoints
4. As a result of #2 and #3, the CP Web API also has this two-tiered session arrangement: The first tier is the read-only Portal session, and the second tier is the brokerage session through which you can talk to /iserver and actually trade the account(s), etc.
5. After logging in with OAuth without competing sessions, you will have a Portal session and can visit non-iserver resources. The additional [/iserver/auth/ssodh/init](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#ssodh-init) endpoint is used to subsequently reopen a brokerage session with our backend, through which you can access the protected /iserver endpoints.

- The Client Portal Gateway will automatically initialize the brokerage session.

6. The brokerage session is associated with the credentials in use – your username – so you don’t need to select an account here. Rather, once you have access to a brokerage session, you can manipulate all accounts visible/accessible to the username in use.
7. Non-iserver endpoints like /portfolio are served by different backend processes that do not require trading permissions and are accessible without a brokerage session
