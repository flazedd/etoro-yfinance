### Request Profit & Loss Copy Location

#### Profit & Loss Request

###### Topic:

**spl**  
 Subscribes the user to live profit and loss information.

###### Arguments:

Do not pass arguments

```
spl+{}
```

#### Order Updates Response

**topic:** String.  
 Returns the topic of the given request.

**args:** Object.  
 Returns the object containing the pnl data.

**acctId.Core:** Object.  
 Specifies the account for which data was requested.

**rowType:** int.  
 The row value of the request. Will increment with additional accounts.

**dpl:** float.  
 Daily Profit and Loss value.

**nl:** float.  
 Net Liquidity in the account.

**upl:** float.  
 Unrealized Profit and Loss for the day.

**uel:** float.  
 Unrounded Excess Liquidty in the account.

**mv:** float  
 Market value of held stocks in the account.

```
{ 
   "topic": "spl" , 
    "args": { 
        "acctId.Core": { 
            "rowType":rowType, 
            "dpl":dpl, 
            "nl":nl,
            "upl":upl,
            "uel": uel,
            "mv": mv
        }
    }
}
```
