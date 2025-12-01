---
icon: lucide/key-round
---

# Personal access tokens

Personal Access Tokens (PATs) provide secure authentication for privately deployed applications.

## Overview

Tokens allow you to:

- Authenticate requests to deployed applications
- Control access with scoped permissions
- Restrict tokens to specific environments
- Set expiration dates for enhanced security
- Track usage and audit access

## Token scopes

Tokens can have different permission levels:

**`read`**

: View application configuration and metadata

**`execute`**

: Execute tools and query applications (most common)

**`admin`**

: Full administrative access to environments

## Creating tokens

Create a token with the CLI:

```bash
toolfront tokens create my-token --scope execute
```

> The token value is shown only once. Save it securely!


### Optional restrictions

Restrict tokens to specific environments:

```bash
toolfront tokens create production-token \
  --scope execute \
  --env env-123 \
  --env env-456
```

Set an expiration date:

```bash
toolfront tokens create temp-token \
  --scope read \
  --expires 2025-12-31T23:59:59Z
```

## Managing tokens

### List tokens

View all active tokens:

```bash
toolfront tokens list
```

Include inactive tokens:

```bash
toolfront tokens list --all
```

### View token details

Get information about a specific token:

```bash
toolfront tokens get <token-id>
```

## Token rotation

Rotate tokens regularly to maintain security.

### When to rotate

Rotate tokens when:

- You suspect a token may be compromised
- A team member with token access leaves
- Changing token permissions or restrictions

### How to rotate

Rotate a token:

```bash
toolfront tokens rotate <token-id>
```

Update permissions during rotation:

```bash
toolfront tokens rotate <token-id> \
  --scope admin \
  --expires 2026-01-01T00:00:00Z
```

The new token value is shown once - update it in your applications immediately.

## Revoking tokens

Revoke a token permanently when it's no longer needed:

```bash
toolfront tokens revoke <token-id> --reason "No longer in use"
```

!!! warning
    Revocation cannot be undone. Applications using the revoked token will lose access immediately.

## Using tokens

### Python sdk

```python
from toolfront import Application

app = Application(
    url="https://your-app.toolfront.app",
    param="token=tf_abc123xyz..."
)

result = app.ask("Your query", model="openai:gpt-5")
```

### Command line

```bash
toolfront ask https://your-app.toolfront.app "Your query" \
  --param "token=tf_abc123xyz..." \
  --model "openai:gpt-5"
```

### MCP server

```json title="claude_desktop_config.json"
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": [
        "toolfront",
        "mcp",
        "https://your-app.toolfront.app",
        "--param", "token=tf_abc123xyz..."
      ]
    }
  }
}
```


!!! question "Learn More"

    See the [CLI reference](../../reference/client_library/cli_commands.md#toolfront-tokens) for more details on token management commands.