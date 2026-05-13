### HMDS Period & Bar Size Copy Location

#### Valid Period Units:

| Unit | Description |
| --- | --- |
| S | Seconds |
| d | Day |
| w | Week |
| m | Month |
| y | Year |

Note: These units are case sensitive.

#### Valid Bar Units:

| Duration | Bar units allowed | Bar size Interval (Min/Max) |
| --- | --- | --- |
| 60 S | secs | mins | 1 secs -> 1mins |
| 3600 S (1hour) | secs | mins | hrs | 5 secs -> 1 hours |
| 14400 S (4hours) | sec | mins | hrs | 10 secs -> 4 hrs |
| 28800 S  (8hours) | sec | mins | hrs | 30 secs -> 8 hrs |
| 1 d | mins | hrs   | d | 1 mins-> 1 day |
| 1 w | mins | hrs | d | w | 3 mins -> 1 week |
| 1 m | mins | d | w | 30 mins -> 1 month |
| 1 y | d | w | m | 1 d -> 1 m |

Note: These units are case sensitive.

**NOTE**: Keep in mind that a step size is defined as the ratio between the historical data request’s duration period and its granularity (i.e. bar size). Historical Data requests need to be assembled in such a way that only a few thousand bars are returned at a time.
