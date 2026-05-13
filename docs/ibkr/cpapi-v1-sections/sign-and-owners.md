### Signatures and Owners Copy Location

Receive a list of all applicant names on the account and for which account and entity is represented.

`GET /acesws/{{ accountID }}/signatures-and-owners`

#### Request Object

###### Path Params

**accountId:** String. Required  
 Pass the account identifier to receive information for.  
 Valid Structure: “U1234567”

- Python
- cURL

```
request_url = f"{baseUrl}/acesws/U1234567/signatures-and-owners"
request.get(url=request_url)
```

```
curl \
--url {{baseUrl}}/acesws/U1234567/signatures-and-owners \
--request GET
```

#### Response Object

**accountId:** String.  
 Specified account identifier in the request.

**users:** Array of Objects.  
 Returns all usernames and their information affiliated with the account.  
 [{  
 **roleId:** String.  
 Returns the role of the username as it relates to the account.

**hasRightCodeInd:** bool.  
 Internal use only.

**username:** String.  
 Returns the username for the particular user under the account.

**entity:** Object.  
 Provides information about the particular entity.  
 {  
 **firstName:** String.  
 Returns the first name of the user.

**lastName:** String.  
 Returns the last name of the user.

**entityType:** String.  
 Returns the type of entity assigned to the user.  
 Valid Value: “INDIVIDUAL”, “Joint”, “ORG”

**entityName:** String.  
 Returns the full entity’s name, concatenating the first and last name fields.  
 }}]

**applicant:** Object.  
 Provides information about the individual listed for the account.  
 {  
 **signatures:** Array of Strings.  
 Returns all names attached to the account.  
 }

```
{
  "accountId": "U1234567",
  "users": [
    {
      "roleId": "OWNER",
      "hasRightCodeInd": true,
      "userName": "user1234",
      "entity": {
        "firstName": "John",
        "lastName": "Smith",
        "entityType": "INDIVIDUAL",
        "entityName": "John Smith"
      }
    },
    {
      "roleId": "Trustee",
      "hasRightCodeInd": False,
      "userName": "user5678",
      "entity": {
        "firstName": "Jane",
        "lastName": "Doe",
        "entityType": "INDIVIDUAL",
        "entityName": "Jane Doe"
      }
    }
  ],
  "applicant": {
    "signatures": [
      "John Smith",
      "Jane Doe"
    ]
  }
}
```
