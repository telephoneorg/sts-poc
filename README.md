# STS GraphQL Server
https://897qfp0jei.execute-api.us-east-1.amazonaws.com/dev/graphql


## Instructions
* use graphql-playground desktop app: https://github.com/prisma/graphql-playground
* use url from below
* set http headers: `{"Authorization": "Bearer {JWT_HERE}"}`

### Locally
* `python3 ./app.py`
* goto http://127.0.0.1:5000/graphql

### Dev
* goto https://897qfp0jei.execute-api.us-east-1.amazonaws.com/dev/graphql


## Learn
* run CreateUser mutation from below with query variables just below it
* same with UpdateUser mutation
* run GetMe query (at any time to see your user)
* run UpdateUserProfile mutation ... using profile id from last query
* run UpdateUserNotificationPolicy mutation ... using notificationPolicy id ...
* trim these queries and mutations down to only what you need, I added everything I could so it would be easier to trim away to what you need.


## Graphql API

### Queries

#### Me

```graphql
query GetMe {
  me {
    id
    firstName
    lastName
    email
    cellPhone
    notificationPolicy {
      id
      allowEmail
      allowSms
      allowMarketing
      created
      updated
    }
    identities {
      edges {
        node {
          id
          provider
          subject
          created
          updated
        }
      }
    }
    contexts {
      edges {
        node {
          id
          type
          status
          profile {
            id
            displayName
            avatar
            bio
            created
            updated
          }
        }
      }
    }
    created
    updated
  }
}
```

#### Node
```graphql
{ node(id: "{ANY_ID_HERE}") }
```

### Mutations

#### CreateUser

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    ok
    user {
      id
      firstName
      lastName
      email
      cellPhone
      created
      updated
      identities {
        edges {
          node {
            id
            provider
            subject
            created
            updated
          }
        }
      }
      notificationPolicy {
        id
        allowEmail
        allowSms
        allowMarketing
        created
        updated
      }
      contexts {
        edges {
          node {
            id
            type
            status
            profile {
              id
              displayName
              avatar
              bio
              created
              updated
            }
          }
        }
      }
    }
  }
}
```

```json
{"input": {"firstName": "Joe", "lastName": "Black", "cellPhone": "+14155552671"}}
```

#### UpdateUser

```graphql
mutation UpdateMyUser($input: UpdateUserInput!) {
  updateUser(input: $input) {
    ok
    user {
      id
      firstName
      lastName
      email
      cellPhone
      created
      updated
      identities {
        edges {
          node {
            id
            provider
            subject
            created
            updated
          }
        }
      }
      notificationPolicy {
        id
        allowEmail
        allowSms
        allowMarketing
        created
        updated
      }
      contexts {
        edges {
          node {
            id
            type
            status
            profile {
              id
              displayName
              avatar
              bio
              created
              updated
            }
          }
        }
      }
    }
  }
}
```

```json
{"input": {"firstName": "Joe New"}}
```

#### UpdateUserProfile
```graphql
mutation UpdateMyUserProfile($input: UpdateUserProfileInput!) {
  updateUserProfile(input: $input) {
    ok
    profile {
      id
      displayName
      avatar
      bio
      created
      updated
    }
  }
}
```

```json
{"input": {"id": "VXNlclByb2ZpbGU6MQ==", "displayName": "Joe Nickname"}}
```

#### UpdateUserNotificationPolicy
```graphql
mutation UpdateMyUserNotificationPolicy($input: UpdateUserNotificationPolicyInput!) {
  updateUserNotificationPolicy(input: $input) {
    ok
    notificationPolicy {
      id
      allowSms
      allowEmail
      allowMarketing
      created
      updated
    }
  }
}
```

```json
{"input": {"id": "{NOTIFICATION_PROFILE_ID}", "allowSms": false}}
```
