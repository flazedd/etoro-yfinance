### Diffie-Hellman Random Value Copy Location

The Diffie-Hellman random value is simply any positive random 256-bit integer value.

This will be used immediately for the Diffie-Hellman challenge as well as the computation of the live session token.

- Python
- C#

```
dh_random = str(random.getrandbits(256))
```

```
Random random = new();

BigInteger dh_random = random.Next(1, int.MaxValue);
```
