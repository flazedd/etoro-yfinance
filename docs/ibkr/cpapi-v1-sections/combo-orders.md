### Combo / Spread Orders Copy Location

Combination orders or spread orders may also be placed using the same orders endpoint. In the case of combo orders, we must use the ‘conidex’ instead of “conid”. The conidex field is a string representation of our combo order parameters.

**Combo Orders follow the format of: ‘{spread\_conid};;;{leg\_conid1}/{ratio},{leg\_conid2}/{ratio}‘**

The spread\_conid is a unique identified used to denote a spread order.  For US Stock Combos, only the spread\_conid needs to be submitted.. For all other countries, you will need to use the format ‘spread\_conid@exchange’.

###### *Available currency spread conids:*

| Currency | Spread ConID |
| --- | --- |
| AUD | 61227077 |
| CAD | 61227082 |
| CHF | 61227087 |
| CNH | 136000441 |
| GBP | 58666491 |
| HKD | 61227072 |
| INR | 136000444 |
| JPY | 61227069 |
| KRW | 136000424 |
| MXN | 136000449 |
| SEK | 136000429 |
| SGD | 426116555 |
| USD | 28812380 |

Following our spread\_conid, we will then follow with 3 semicolons, and then the first leg\_coind. This will be the first contract to trade. After the conid, a forward slash, ‘/’, needs to be included followed by your spread ratio.

The ratio indicates two parts. The first is the sign of the ratio, whether it is positive or negative. Positive signs indicate a ‘Buy’ side, while a negative value represents a ‘Sell’ side. This could also be explained as a state of ‘Long’ and ‘Short’ respectively, depending on your current position and intention. After indicating the side, you would indicate the ratio value. This is the multiplier of your quantity value.

Now, you can continue to add legs to the order by separating them with a comma. The number of legs available is based on the exchange’s rules.

#### Combo Order Pricing

Combo orders can submit their price values based on the value of the individual leg, multiplied by the ratio. Each leg is then added together to create the final price of the order.

These prices can end as negative values if one of the legs is being sold and the total value of that leg multiplied by the ratio is greater than the value of the other order.

The price of a combo order = [({Cost of Leg 1} \* {The ratio of Leg 1}) + ({Cost of Leg n} \* {Ratio of Leg n}) + ({Cost of Leg n+1} \* {Ratio of Leg n+1})]
