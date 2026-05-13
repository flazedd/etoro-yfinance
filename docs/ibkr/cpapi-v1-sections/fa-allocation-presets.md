### Allocation Preset Combinations Copy Location

In order to attain specific allocation behaviors, a combination of various settings must be specified. The tables below detail what settings must be used.Interactive Brokers supports two forms of allocation methods. Allocation methods that have calculations completed by Interactive Brokers, and a set of allocation methods calculated by the user and then specified.

The preset settings are based on the Advisor Presets setting built in TWS.  
 Every time a user logs in to TWS, the presets established in the CPAPI will update to reflect the settings in TWS.  
 Presets adjusted in the Client Portal API will not adjust the settings in TWS.

#### IB-computed allocation methods

| Intended Behavior | Proportional Allocation | Closing Behavior |
| --- | --- | --- |
| Make positions be proportional based on method | group\_proportional\_allocation=false | group\_auto\_close\_positions=true |
| Distribute shares based on method selected | group\_proportional\_allocation=true | group\_auto\_close\_positions=true |
| Distribute shares based on method selected, do not prioritize accounts that are closing position | group\_proportional\_allocation=true | group\_auto\_close\_positions=false |

#### User-specified allocation methods

###### Formerly known as Allocation Profiles

| Intended Behavior | Closing Behavior |
| --- | --- |
| Distribute shares based on method selected | profile\_auto\_close\_positions=true |
| Distribute shares based on method selected, do not prioritize accounts that are closing position | profile\_auto\_close\_positions=false |
