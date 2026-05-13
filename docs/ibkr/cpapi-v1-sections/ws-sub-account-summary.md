### Subscribe Account Summary Copy Location

#### Subscribe to Account Summary Topic

###### Topic:

**ssd**  
 Subscribes to a stream of account summary messages for the specified account.

###### Topic Target:

**accountId:** Required.  
 Must pass the account ID whose account summary data will be subscribed.

###### Parameters:

{  
 **keys:** Array of Strings.  
 Pass specific account summary data keys to receive messages concerning only those keys. Passing no named keys when opening the subscription will deliver account summary messages containing values for the selected account.  
 Example Values: “AccruedCash-S”, “ExcessLiquidity-S”

**fields:** Array of Strings.  
 Pass specific account summary field names to filter responses to include only these fields for the requested keys. Passing no named fields when opening the subscription will deliver all available data points for the specified account summary keys.  
 Example Values: “currency”, “monetaryValue”  
 }

```
ssd+DU1234567+{
    "keys":["AccruedCash-S","ExcessLiquidity-S"],
    "fields":["currency","monetaryValue"]
}
```

#### Account Summary Topic Messages

{  
 **result:** Array of JSON objects, each corresponding to an account summary value for the account.  
   [  
     {  
 **key:** String.  
 The name of the account summary value.  
 This is always returned.

**timestamp:** Number (integer only).  
 The timestamp reflecting when the value was retrieved.  
 This is always returned.

**value:** String.  
 A non-monetary value associated with the key. This may include dates, account titles, or other relevant information.

**monetaryValue:** Number.  
 A monetary value associated with the key. Returned when the key pertains to pricing or balance details.

**currency:** String.  
 The currency reflected by monetaryValue.  
 Example Value: “USD”, “EUR”, “HKD”

**severity:** Number (integer only).  
 Internal use only.  
     },  
     …  
   ]  
 }

```
{"result":[
    {
     "key":"key1",
     "currency":"currency", 
     "monetaryValue":monetaryValue, 
     "severity":0, 
     "timestamp":timestamp
    },
    {
     "key":"key2",
     "currency":"currency", 
     "value":value, 
     "severity":0, 
     "timestamp":timestamp
    },
]}
```
