### Unsubscribe Account Ledger Copy Location

#### Unsubscribe from Account Ledger Topic

###### Topic:

**uld**  
 Unsubscribes from account ledger messages for the specified account.

###### Topic Target:

**accountId:** Required.  
 Must pass the account ID whose ledger messages will be unsubscribed.

###### Parameters:

none

```
uld+DU1234567+{}
```

#### Account Ledger Unsubscribe Message

Arrives once.

{  
 **result:** String.  
 Confirms successful unsubscription.  
 }

```
{"result":"unsubscribed from ledger"}
```
