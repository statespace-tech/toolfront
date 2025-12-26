---
icon: lucide/lock
---

!!! info "First time?"

    Create a free [Statespace](https://statespace.com) account to get your API key.

# Access tokens

Access tokens authenticate requests to private applications.

## Quick start

1. Deploy a private app with `$ toolfront app deploy ./project --private`

2. Get an access token with `toolfront token create`

3. `curl` your app with the access token

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR-TOKEN" \
  https://127.0.0.1:8000/README.md
```

## CLI reference

### `toolfront token create`

Generate a new access token for authenticating requests to private apps.

**Usage:**

```bash
toolfront token create [OPTIONS]
```

**Options:**

`--name`

: Optional name to identify the token

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

### `toolfront token list`

View all your access tokens.

**Usage:**

```bash
toolfront token list [OPTIONS]
```

**Options:**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

### `toolfront token revoke`

Revoke an access token to prevent further use.

**Usage:**

```bash
toolfront token revoke [OPTIONS] TOKEN_ID
```

**Arguments:**

`TOKEN_ID`

: ID of token to revoke

**Options:**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--yes, -y`

: Skip confirmation prompt

!!! warning "Security"
    Keep tokens secure and never commit them to version control