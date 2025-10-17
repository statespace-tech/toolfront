# MCP Server

ToolFront's MCP server provides environment connectivity and browsing tools to your agents.

=== ":material-code-json:{ .middle } &nbsp; JSON"

    Configure MCP clients like Claude Desktop or Cline.

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", "file:///path/environment"]
        }
      }
    }
    ```

=== ":material-console:{ .middle } &nbsp; CLI"

    Run the server directly from the command line.

    ```bash
    toolfront mcp file:///path/environment
    ```

Available options:

- `--transport` - Communication protocol: `stdio` (default), `streamable-http`, or `sse`
- `--host` - Server host address (default: `127.0.0.1`)
- `--port` - Server port number (default: `8000`)
- `--params` / `-p` - Authentication for remote environment (e.g., `--params KEY=value`)
- `--env` - Environment variables for tools (e.g., `--env TOKEN=value`)

---

## Core Tools

Agents use six core tools to interact with environments:

- :material-play:{ .middle } `execute` - Execute tools commands in frontmatters, optionally passing parameters
- :material-eye:{ .middle } `read` - Read the content of a specific file
- :material-file-tree:{ .middle } `tree` - View directory structure
- :material-folder-search:{ .middle } `glob` - List files matching a glob pattern
- :material-regex:{ .middle } `grep` - Search files using regex patterns
- :material-magnify:{ .middle } `search` - Find relevant documents with BM25 search

!!! toolfront "Search Tool"

    Environments deployed with **[ToolFront Cloud](toolfront_cloud.md)** are automatically indexed and get access to the `search` tool:

    ```
    Let me search the environment for documents relevant to "ticket pricing API"...

    Found 3 relevant pages:
      - ./api/pricing.md (highly relevant)
      - ./guides/analytics.md (relevant)
      - ./examples/queries.md (somewhat relevant)

    I'll start by reading ./api/pricing.md...
    ```

---

## Environment Variables

Environment tools may reference environment variables for authentication or configuration:

```markdown
---
tools:
  - [curl, -X, GET, "https://api.com/data", -H, "Authorization: Bearer $TOKEN"]
  - [toolfront, database, $DB_URL]
  
---

# My Markdown page
...
```

Pass these variables when starting the MCP server:

=== ":material-code-json:{ .middle } &nbsp; JSON"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", "file:///path/environment"],
          "env": {
            "TOKEN": "token",
            "DB_URL": "postgresql://user:pass@localhost:5432/mydb"
          }
        }
      }
    }
    ```

=== ":material-console:{ .middle } &nbsp; CLI"

    ```bash
    toolfront mcp file:///path/environment \
      --env "TOKEN=token" \
      --env "DB_URL=postgresql://user:pass@localhost:5432/mydb"
    ```

::: toolfront.cli.mcp.serve
    options:
      show_root_heading: true
      show_source: true