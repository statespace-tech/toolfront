---
icon: lucide/terminal
---

# ToolFront CLI

Full CLI syntax, arguments, and options.

## [`toolfront ask`](#toolfront-ask)

Query a running application.

**Usage**

```bash
toolfront ask [OPTIONS] URL PROMPT
```

**Arguments**

`URL`

: URL of running application

`PROMPT`

: Query prompt

**Options**

`--model`

: AI model for query, using the provider:model format (e.g., `openai:gpt-5`)

`--param`

: Authentication parameter for the remote application (KEY=VALUE)

`--env`

: Environment variables to pass to commands (KEY=VALUE)

`--verbose`

: Show verbose output

## [`toolfront mcp`](#toolfront-serve)

Start an MCP (Model Context Protocol) server for your application.

**Usage**

```bash
toolfront mcp [OPTIONS] URL
```

**Arguments**

`URL`

: URL of application to connect to

**Options**

`--param`, `-p`

: Authentication parameters (KEY=VALUE, can be repeated)

`--env`

: Environment variables to pass to commands (KEY=VALUE)

`--host`

: Server host address (default: `127.0.0.1`)

`--port`

: Server port number (default: `8000`)

`--transport`

: Transport mode: `stdio`, `streamable-http`, or `sse` (default: `stdio`)

`--log-level`

: Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` (default: `WARNING`)

## [`toolfront serve`](#toolfront-serve)

Run your application locally for development and testing.

**Usage**

```bash
toolfront serve [OPTIONS] PATH
```

**Arguments**

`PATH`

: Path to application repository

**Options**

`--host`

: Host to bind the server to (default: `127.0.0.1`)

`--port`

: Port to bind the server to (default: `8000`)

## [`toolfront deploy`](#toolfront-serve)

Deploy your application to the cloud and get a shareable URL.

**Usage**

```bash
toolfront deploy [OPTIONS] PATH
```

**Arguments**

`PATH`

: Path to application repository

**Options**

`--name`

: Custom environment name (defaults to directory name)

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--verify`

: Wait and verify environment is accessible after deployment

## [`toolfront list`](#toolfront-list)

View all your deployed applications.

**Usage**

```bash
toolfront list [OPTIONS]
```

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

## [`toolfront update`](#toolfront-serve)

Update an existing deployment with new markdown files.

**Usage**

```bash
toolfront update [OPTIONS] DEPLOYMENT_ID PATH
```

**Arguments**

`DEPLOYMENT_ID`

: ID of app to update

`PATH`

: Path to application repository

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

## [`toolfront delete`](#toolfront-serve)

Remove a deployment from the cloud.

**Usage**

```bash
toolfront delete [OPTIONS] DEPLOYMENT_ID
```

**Arguments**

`DEPLOYMENT_ID`

: ID of app to update

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--yes`, `-y`

: Skip confirmation prompt

## [`toolfront tokens`](#toolfront-tokens)

Manage Personal Access Tokens for authentication.

### [`toolfront tokens create`](#toolfront-tokens-create)

Create a new Personal Access Token.

**Usage**

```bash
toolfront tokens create [OPTIONS] NAME
```

**Arguments**

`NAME`

: Name for the token

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--org-id`

: Organization ID (overrides config)

`--scope`

: Token scope: `read`, `execute`, or `admin` (default: `execute`)

`--env`

: Restrict to specific environment IDs (can be repeated)

`--expires`

: Expiration date (ISO 8601 format)

### [`toolfront tokens list`](#toolfront-tokens-list)

List all Personal Access Tokens.

**Usage**

```bash
toolfront tokens list [OPTIONS]
```

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--org-id`

: Organization ID (overrides config)

`--all`

: Show inactive tokens too

`--limit`

: Maximum number of tokens to return (default: `100`)

### [`toolfront tokens get`](#toolfront-tokens-get)

Get details for a specific token.

**Usage**

```bash
toolfront tokens get [OPTIONS] TOKEN_ID
```

**Arguments**

`TOKEN_ID`

: ID of the token

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

### [`toolfront tokens rotate`](#toolfront-tokens-rotate)

Rotate a token (generates new token value, revokes old one).

**Usage**

```bash
toolfront tokens rotate [OPTIONS] TOKEN_ID
```

**Arguments**

`TOKEN_ID`

: ID of the token to rotate

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--name`

: New name for the token

`--scope`

: New scope: `read`, `execute`, or `admin`

`--env`

: New environment restrictions (can be repeated)

`--expires`

: New expiration date (ISO 8601 format)

### [`toolfront tokens revoke`](#toolfront-tokens-revoke)

Revoke a token (cannot be undone).

**Usage**

```bash
toolfront tokens revoke [OPTIONS] TOKEN_ID
```

**Arguments**

`TOKEN_ID`

: ID of the token to revoke

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--reason`

: Reason for revocation
