---
icon: lucide/terminal
---

# Commands

The ToolFront CLI provides commands for running, deploying, and managing your AI applications.

---

## `toolfront serve`

Run your application locally for development and testing.

```bash
toolfront serve [PATH] [OPTIONS]
```

**Options**

`--host`

: Host to bind the server to (default: 127.0.0.1)

`--port`

: Port to bind the server to (default: 8000)

---

## `toolfront deploy`

Deploy your application to the cloud and get a shareable URL.

```bash
toolfront deploy [PATH] [OPTIONS]
```

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

## `toolfront list`

View all your deployed applications.

```bash
toolfront list [OPTIONS]
```

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

---

## `toolfront update`

Update an existing deployment with new markdown files.

```bash
toolfront update [DEPLOYMENT_ID] [PATH] [OPTIONS]
```

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

---

## `toolfront delete`

Remove a deployment from the cloud.

```bash
toolfront delete [DEPLOYMENT_ID] [OPTIONS]
```

**Options**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--yes`, `-y`

: Skip confirmation prompt

---

## `toolfront mcp`

Start an MCP (Model Context Protocol) server for your application.

```bash
toolfront mcp [URL] [OPTIONS]
```

**Options**

`--param`, `-p`

: Authentication parameters (KEY=VALUE, can be repeated)

`--env`

: Environment variables to pass to commands (KEY=VALUE)

`--host`

: Server host address (default: 127.0.0.1)

`--port`

: Server port number (default: 8000)

`--transport`

: Transport mode: stdio, streamable-http, or sse (default: stdio)
