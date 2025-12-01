---
icon: simple/modelcontextprotocol
---

# MCP server

ToolFront's MCP (Model Context Protocol) server exposes your applications as tools.

## Basic usage

Start the MCP server with your application's URL using `uvx`.

```bash
uvx toolfront mcp http://127.0.0.1:8000
```

## Client configuration

Add ToolFront to your MCP client configuration file.

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": ["toolfront", "mcp", "http://127.0.0.1:8000"]
    }
  }
}
```

## Authentication

Pass authentication parameters for private applications.

```bash
uvx toolfront mcp https://cloud.statespace.com/you/my-app \
  --param "Authorization=Bearer your-token-here"
```


## Environment variables

Provide environment variables to your application's tools.

```bash
uvx toolfront mcp http://127.0.0.1:8000 \
  --env "DATABASE_URL=postgres://localhost/mydb" \
  --env "API_KEY=secret-key"
```

You can also configure environment variables in your client configuration:

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": ["toolfront", "mcp", "http://127.0.0.1:8000"],
      "env": {
        "DATABASE_URL": "postgres://localhost/mydb",
        "API_KEY": "secret-key"
      }
    }
  }
}
```

!!! question "Learn more"
    See the [Tools documentation](../application/tools.md#environment-variables) for how to define environment variables in your tool configurations.

## Command options

Available options for the `mcp` command:

| Option | Default | Description |
|--------|---------|-------------|
| `--transport` | `stdio` | Communication protocol: `stdio`, `streamable-http`, or `sse` |
| `--host` | `127.0.0.1` | Server host address |
| `--port` | `8000` | Server port number |
| `--param` / `-p` | None | Authentication parameters (can be repeated) |
| `--env` | None | Environment variables for tools (can be repeated) |
| `--log-level` | `WARNING` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |

!!! question "Learn more"
    See the [CLI commands documentation](../../reference/client_library/cli_commands.md) for complete command syntax and options.

