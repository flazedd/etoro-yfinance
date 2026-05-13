### Executions and Netting Copy Location

Positions in forecast contracts are opened by buying either a YES or NO contract. Positions are reduced or closed by buying the opposite contract at the same strike: NO reduces YES, and YES reduces NO.  
 An opening order will receive normal Bought/Bot execution reports (“side”: “B”). However, if an account is already long YES or NO, a reduction of that position will produce a series of execution reports.

For example, consider an account long 100 YES contracts. A new order is submitted to buy 10 NO contracts of the same strike. Execution of this Buy NO order will be netted against the long 100 YES position.

- Order receives an execution for 10 NO contracts.
- IB sends an execution report of Bot 10 NO (“side”: “B”). This momentarily creates a long 10 NO position in the account.
- IB sends an execution report of Netting 10 YES (“side”: “N”). This reduces the long 100 YES position in the account by 10, yielding 90.
- IB sends an execution report of Netting 10 NO (“side”: “N”). This reduces the long 10 NO position by 10 to 0, flattening it.
- Net result: Account contains only the long 90 YES position.

The above netting execution reports will arrive within milliseconds of the first Bot execution. IB’s ForecastTrader reflects all such Bot & Netting executions as separate trades in the account’s Trade History.

Note that it is also possible to change the side of a position from YES to NO via a single opposite-side buy order.

For example, consider the same account, now long 90 YES. Another order is submitted to buy 130 NO contracts on the same strike.

- Order receives an execution for 130 NO contracts.
- IB sends an execution report of Bot 130 NO (“side”: “B”). This momentarily creates a long 130 NO position in the account.
- IB sends an execution report of Netting 90 YES (“side”: “N”). This reduces the long 90 YES position in the account to 0, flattening it.
- IB sends an execution report of Netting 90 NO (“side”: “N”). This reduces the the long 130 NO position by 90, yielding 40.
- Net result: Account contains only the long 40 NO position.
