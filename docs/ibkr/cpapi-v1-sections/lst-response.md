### Response Copy Location

**diffie\_hellman\_response:** String.  
 Response based on the calculated Diffie Hellman challenge.  
 The full value should be 512 characters long.

**live\_session\_token\_signature:** String.  
 Signature value used to prove authenticated status for subsequent requests.

**live\_session\_token\_expiration:** Number.  
 Returns the epoch timestamp of the live session token’s expiration.  
 The live session token is valid for approximately 24 hours after creation.

```
{
  "diffie_hellman_response": "62933e{...}d64d6db34d",
"live_session_token_signature": "9bd5922b2b79effef23c6fb03cc715dcdc8d6219",
"live_session_token_expiration": 1700691802316
}
```
