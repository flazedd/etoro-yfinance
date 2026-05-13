### Unsubscribe Account Summary Copy Location

#### Unsubscribe from Account Summary Topic

###### Topic:

**usd**  
 Unsubscribes the user from account summary information for the specified account.

###### Topic Target:

**accountId:** Required.  
 Must pass the account ID whose account summary messages will be unsubscribed.

###### Parameters:

none

```
usd+DU1234567+{}
```

#### Account Summary Unsubscribe Message

Arrives once.

{  
 **result:** String.  
 Confirms successful unsubscription.  
 }

```
{"result":"unsubscribed from summary"}
```
