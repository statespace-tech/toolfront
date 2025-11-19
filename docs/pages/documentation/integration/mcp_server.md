---
icon: simple/modelcontextprotocol
---

# MCP server

ToolFront's MCP (Model Context Protocol) server exposes your applications as tools for MCP-compatible agents like Cursor, Claude Desktop, and Cline.

## Running

Run the server with `uvx`

```bash
uvx toolfront mcp  http://127.0.0.1:8000
```

The following options are available:

- `--transport` - Communication protocol: `stdio` (default), `streamable-http`, or `sse`
- `--host` - Server host address (default: `127.0.0.1`)
- `--port` - Server port number (default: `8000`)
- `--params` / `-p` - Authentication for remote application (e.g., `--params KEY=value`)
- `--env` - Environment variables for tools (e.g., `--env TOKEN=value`)

!!! example "Using Authentication and Environment Variables"

    For private deployments with authentication:

    ```bash
    uvx toolfront mcp https://cloud.statespace.com/you/my-app \
      --params "Authorization=Bearer your-token-here"
    ```

    To pass environment variables to your application's tools:

    ```bash
    uvx toolfront mcp http://127.0.0.1:8000 \
      --env "DATABASE_URL=postgres://localhost/mydb" \
      --env "API_KEY=secret-key"
    ```

    Combining both:

    ```bash
    uvx toolfront mcp https://cloud.statespace.com/you/my-app \
      --params "Authorization=Bearer your-token" \
      --env "STRIPE_KEY=sk_test_123" \
      --env "OPENAI_API_KEY=sk-proj-456"
    ```

## Client Configuration

Can configure MCP clients like Cursor, Claude Desktop or Cline as follows:

```json
{
    "mcpServers": {
    "toolfront": {
        "command": "uvx",
        "args": ["toolfront", "mcp", " http://127.0.0.1:8000"]
    }
    }
}
```


## Running the MCP Server

Start with `uvx` (no install needed):

```bash
uvx toolfront mcp http://127.0.0.1:8000
# Stdio server ready
```

Options:
- `--transport stdio` (default: for terminals/IDEs), `streamable-http`, `sse`.
- `--host 0.0.0.0 --port 8001`: Bind address.
- `--param KEY=val`: Auth for remote apps (e.g., `--param Authorization=Bearer token`).
- `--env VAR=val`: Tool env (e.g., `--env DB_URL=postgres://...`).

From `application.py`: Wraps MCPServerStdio with retries (3x), timeout (30s).

### Local Example

1. Serve app: `toolfront serve .`
2. MCP: `uvx toolfront mcp http://127.0.0.1:8000 --transport stdio`

Query in IDE: "Use the toolfront server to check status."

### Remote with Auth

```bash
uvx toolfront mcp https://myapp.toolfront.app \
  --param "Authorization=Bearer sk-..." \
  --env "API_KEY=secret"
```

## Client Configuration

Add to your MCP config (e.g., `~/.cursor/mcp.json` or Claude settings):

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": [
        "toolfront",
        "mcp",
        "http://127.0.0.1:8000",
        "--transport", "stdio"
      ],
      "env": {
        "DB_URL": "postgres://..."
      }
    }
  }
}
```

- **Cursor**: Restart after config; tools appear in composer.
- **Claude Desktop**: Edit `claude_desktop_config.json`.
- **Cline**: Similar JSON setup.

Test: Ask "What tools does toolfront provide?" – should list from app.

## Transports Explained

- **Stdio** (default): For local/terminal; bidirectional pipe.
- **Streamable-HTTP**: For web/IDEs; SSE-like streaming.
- **SSE**: Server-Sent Events for real-time.

Switch: `--transport streamable-http --host 0.0.0.0 --port 8001`. Access: `http://localhost:8001`.

## Troubleshooting

- **No tools discovered?** Ensure app served; check logs for "Instructions from URL".
- **Auth fails?** Verify `--param` matches app's expected headers (from `application.py` param).
- **Timeout?** Increase via env or custom MCPServerStdio in code.
- **Stdio vs HTTP?** Stdio for local (faster); HTTP for remote/networked setups.
- **Retries?** Built-in 3x; verbose: Add `--verbose` if CLI-wrapped.

> Build apps first: [Your First App](../getting_started/first_app.md). SDK alternative: [Python SDK](../guides/python_sdk.md).