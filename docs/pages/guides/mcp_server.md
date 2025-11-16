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