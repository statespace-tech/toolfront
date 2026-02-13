---
icon: lucide/lock
---

!!! info "First time?"

    Create a free [Statespace](https://statespace.com) account to get your API key.

# Access tokens

Access tokens authenticate requests to private applications.

## Quick start

1. Deploy a private app with `statespace app create ./project --visibility private`

2. Log in and fetch your API key with `statespace auth login` and `statespace auth token`

3. `curl` your app with the access token

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR-TOKEN" \
  https://your-app.app.statespace.com/README.md
```

## CLI reference

### `statespace auth login`

Authenticate and store credentials locally.

```bash
statespace auth login
```

### `statespace auth token`

Print the current API token for authenticated requests.

```bash
statespace auth token
```

!!! warning "Security"
    Keep tokens secure and never commit them to version control
