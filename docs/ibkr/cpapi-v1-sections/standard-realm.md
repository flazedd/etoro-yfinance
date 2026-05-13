### Realm Copy Location

The realm is a required oauth parameter. The realm will only ever be one of two values.

If you are using the “TESTCONS” consumer key during your paper testing, you will need to use “test\_realm”

- Python
- C#

```
# Oauth realm param omitted from signature, added to header afterward.
oauth_params["realm"] = "test_realm"
```

```
// Oauth realm param omitted from signature, added to header afterward.
oauth_params.Add("realm", :"test_realm");
```

Once you are using your own consumer key, you must use “limited\_poa”.

- Python
- C#

```
# Oauth realm param omitted from signature, added to header afterward.
oauth_params["realm"] = "limited_poa"
```

```
// Oauth realm param omitted from signature, added to header afterward.
oauth_params.Add("realm", :"limited_poa");
```
