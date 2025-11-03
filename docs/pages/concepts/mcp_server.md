---
icon: simple/modelcontextprotocol
---

# MCP server

ToolFront's MCP (Model Context Protocol) server exposes your applications as tools for AI agents in MCP-compatible clients like Cursor, Claude Desktop, and Cline.

## Running the server

```bash
toolfront mcp  http://127.0.0.1:8000
```

The following options are available:

- `--transport` - Communication protocol: `stdio` (default), `streamable-http`, or `sse`
- `--host` - Server host address (default: `127.0.0.1`)
- `--port` - Server port number (default: `8000`)
- `--params` / `-p` - Authentication for remote application (e.g., `--params KEY=value`)
- `--env` - Environment variables for tools (e.g., `--env TOKEN=value`)

## Configuring the client

Can configure MCP clients like Claude Desktop or Cline as follows:

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