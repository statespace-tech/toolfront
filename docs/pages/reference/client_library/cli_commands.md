---
icon: lucide/terminal
---

# ToolFront CLI

Full CLI syntax, arguments, and options.

---

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

---

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

---

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

---

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

---

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

---

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

---

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
