### Event Contracts Copy Location

Interactive Brokers models Event Contract instruments on options (for ForecastEx products) and futures options (for CME Group products).

Event Contracts can generally be thought of as options products in the Web API, and their discovery workflow follows a familiar options-like sequence. This guide will make analogies to conventional index options for both ForecastEx and CME Group products.

IB’s Event Contract instrument records use the following fields inherited from the options model:

- An **underlier**, which may or may not be artificial:
  - For **CME products**, a tradable Event Contract will have the relevant CME future as its underlier.
  - For **ForecastEx products**, IB has generated an artificial underlying index which serves as a container for related Event Contracts in the same product class. These artificial indices do not have any associated reference values and are purely an artifact of the option instrument model used to represent these Event Contracts. However, these artificial underlying indices can be used to search for groups of related Event Contracts, just as with index options.
- A **Symbol** value which matches the symbol of the underlier, and which reflects the issuer’s product code.
- A **Trading Class** which also reflects the issuer’s product code for the instrument, and in the case of CME Group products, is used to differentiate Event Contracts from CME futures options.
  - Note that many CME Group Event Contracts, which resolve against CME Group futures, are assigned a Trading Class prefixed with “EC” and followed by the symbol of the relevant futures product, to avoid naming collisions with other derivatives (i.e., proper futures options listed on the same future).
- A **Put or Call (Right)** value, where Call = Yes and Put = No.
  - Note that ForecastEx instruments do not permit Sell orders. Instead, ForecastEx positions are flattened or reduced by buying the opposing contract. CME Group Event Contracts permit both buying and selling.
- An artificial **Contract Month** value, again used primarily for searching and filtering available instruments. Most Event Contract products do not follow monthly series as is common with index or equity options, so these Contract Month values are typically not a meaningful attribute of the instrument. Rather, they permit filtering of instruments by calendar month.
- A **Last Trade Date, Time, and Millisecond** values, which together indicate precisely when trading in an Event Contract will cease, just as with index options.
- An **Expected Resolution Time** when the outcome of the tracked event is published, and contracts are determined to be in or out of the money. This is commonly referred to as the contract’s “expiration date”.
- An **Expected Payout Time** when contracts are settled and removed from accounts. Proceeds are paid out to those expiring in the money.
- A **Measured Period** as defined in the contract’s question. This is the primary date used for organization of contracts (as in an options chain).
- A **Strike** value, which is the numerical value on which the event resolution hinges. Though numerical, this value need not represent a price.
- An **instrument description (or “local symbol”)** in the form `"PRODUCT EXPIRATION STRIKE RIGHT"`, where:
  - `PRODUCT` is the issuer’s product identifier
  - `EXPIRATION` is the date of the instrument’s resolution in the form `MmmDD'YY`, e.g., “Sep26’24”
  - `STRIKE` is the numerical value that determines the contract’s moneyness at expiration
  - `RIGHT` is a value YES or NO
