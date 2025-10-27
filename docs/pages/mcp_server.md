# MCP Server

ToolFront's MCP server provides application connectivity and browsing tools to your agents.

=== ":material-code-json:{ .middle } &nbsp; JSON"

    Configure MCP clients like Claude Desktop or Cline.

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", "file:///path/to/project"]
        }
      }
    }
    ```

=== ":material-console:{ .middle } &nbsp; CLI"

    Run the server directly from the command line.

    ```bash
    toolfront mcp file:///path/to/project
    ```

Available options:

- `--transport` - Communication protocol: `stdio` (default), `streamable-http`, or `sse`
- `--host` - Server host address (default: `127.0.0.1`)
- `--port` - Server port number (default: `8000`)
- `--params` / `-p` - Authentication for remote application (e.g., `--params KEY=value`)
- `--env` - Environment variables for tools (e.g., `--env TOKEN=value`)

---

## Core Tools

Agents use six core tools to interact with applications:

- :material-play:{ .middle } `execute` - Execute tools in frontmatters, optionally passing arguments and parameters
- :material-eye:{ .middle } `read` - Read the content of a specific file
- :material-file-tree:{ .middle } `tree` - View directory structure
- :material-folder-search:{ .middle } `glob` - List files matching a glob pattern
- :material-regex:{ .middle } `grep` - Search files using regex patterns
- :material-magnify:{ .middle } `search` - Find relevant documents with BM25 search

!!! toolfront "Search Tool"

    Applications deployed with **[ToolFront Cloud](toolfront_cloud.md)** are automatically indexed and get access to the `search` tool:

    ```
    Let me search the application for documents relevant to "ticket pricing API"...

    Found 3 relevant pages:
      - ./api/pricing.md (highly relevant)
      - ./guides/analytics.md (relevant)
      - ./examples/queries.md (somewhat relevant)

    I'll start by reading ./api/pricing.md...
    ```

---

::: toolfront.cli.serve
    options:
      show_root_heading: true
      show_source: true