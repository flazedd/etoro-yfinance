### Background regarding CP Web API sessions: Copy Location

1. An IB username can only have one brokerage session (trading-enabled) session open at a time, i.e., it can only trade and use similarly restricted functionality on one platform (TWS, Client Portal, etc.) at any given moment, and switching to trading on a different platform entails closing the existing brokerage session and opening a new one from the new platform.
2. Web API sessions in general are two-tiered:
   - An “outer” prerequisite “read-only session” that is required to be active/valid in order to make any CP Web API request, though by itself it only permits access to **non-/iserver** endpoints.
   - The “brokerage session”, established after the read-only, that permits access to trading, consumption of market data, and all other functionality behind **/iserver** endpoints.
3. This two-tiered arrangement reflects the way our Client Portal website permits you to log into a read-only session for account management when that username is already logged into a brokerage session elsewhere (e.g., TWS), leaving the TWS brokerage session undisturbed.
4. The CPAPI iframe actually behaves like the CP Gateway mentioned frequently in our CP Web API documentation (the Java-based reverse proxy tool for retail clients). The CPAPI iframe will attempt to establish a brokerage session automatically, as soon as a login occurs and the read-only session is created via SSO.
