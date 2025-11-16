---
icon: lucide/play
---

# Command Line

The ToolFront CLI provides commands for running, deploying, and managing your AI applications.

---

## `serve`

Run your application locally for development and testing.

**Usage:** `toolfront serve [PATH] [OPTIONS]`

```bash
toolfront serve ./my-app
```

This starts a local HTTP server that serves your markdown files and executes tool commands.

**Options:**

- `--host` - Host to bind the server to (default: 127.0.0.1)
- `--port` - Port to bind the server to (default: 8000)

Once running, you can interact with your application using the [Python SDK](../python_sdk.md), or [MCP Server](../mcp_server.md).

---

## `deploy`

Deploy your application to the cloud and get a shareable URL.

**Usage:** `toolfront deploy [PATH] [OPTIONS]`

```bash
toolfront deploy ./my-app
```

This scans your markdown files, uploads them to the gateway, and provisions a hosted environment.

**Options:**

- `--name` - Custom environment name (defaults to directory name)
- `--api-key` - Gateway API key (overrides config)
- `--gateway-url` - Gateway base URL (overrides config)
- `--verify` - Wait and verify environment is accessible after deployment

---

## `list`

View all your deployed applications.

**Usage:** `toolfront list [OPTIONS]`

```bash
toolfront list
```

This displays a table of all your deployments with their status, ID, and URL.

**Options:**

- `--api-key` - Gateway API key (overrides config)
- `--gateway-url` - Gateway base URL (overrides config)

---

## `update`

Update an existing deployment with new markdown files.

**Usage:** `toolfront update [DEPLOYMENT_ID] [PATH] [OPTIONS]`

```bash
toolfront update <deployment-id> ./my-app
```

This uploads your latest markdown files to an existing deployment and updates the search index.

**Options:**

- `--api-key` - Gateway API key (overrides config)
- `--gateway-url` - Gateway base URL (overrides config)

---

## `delete`

Remove a deployment from the cloud.

**Usage:** `toolfront delete [DEPLOYMENT_ID] [OPTIONS]`

```bash
toolfront delete <deployment-id>
```

This permanently deletes the specified deployment.

**Options:**

- `--api-key` - Gateway API key (overrides config)
- `--gateway-url` - Gateway base URL (overrides config)
- `--yes`, `-y` - Skip confirmation prompt

---

## `mcp`

Start an MCP (Model Context Protocol) server for your application.

**Usage:** `toolfront mcp [URL] [OPTIONS]`

```bash
toolfront mcp <url>
```

This creates an MCP server that AI assistants can use to interact with your application's tools.

**Options:**

- `--param`, `-p` - Authentication parameters (KEY=VALUE, can be repeated)
- `--env` - Environment variables to pass to commands (KEY=VALUE)
- `--host` - Server host address (default: 127.0.0.1)
- `--port` - Server port number (default: 8000)
- `--transport` - Transport mode: stdio, streamable-http, or sse (default: stdio)
