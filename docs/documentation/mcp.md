# Model Context Protocol (MCP)

ToolFront runs as an MCP server to integrate with AI applications like Claude Desktop, Cursor, and GitHub Copilot.

---

## Configuration

First, create your MCP config file by passing your data source URL in the `args` array:

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-database:{ .middle } &nbsp; Databases"

    ```json linenums="1"
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront[postgres]", // (1)!
            "postgresql://user:pass@host:5432/mydb" // (2)!
          ]
        }
      }
    }
    ```
    
    1. Replace with the necessary database extra
    2. Replace with your actual connection URL

=== ":fontawesome-solid-code:{ .middle } &nbsp; APIs"

    ```json linenums="1"
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront",
            "https://api.example.com/openapi.json" // (1)!
          ]
        }
      }
    }
    ```

    1. OpenAPI specification URL

=== ":fontawesome-solid-file:{ .middle } &nbsp; Documents"

    ```json linenums="1"
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront",
            "/path/to/document.pdf" // (1)!
          ]
        }
      }
    }
    ```
    
    4. Path to document file

</div>

Then, copy-paste your config into your preferred MCP-enabled application.

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-code:{ .middle } &nbsp; Cursor"

    1. Open Cursor settings
    2. Navigate to MCP configuration section
    3. Add the appropriate configuration from the tabs above to your MCP settings file

=== ":simple-claude:{ .middle } &nbsp; Claude Desktop"

    1. Open your home directory
    2. Navigate to `claude_desktop_config.json`
    3. Add the appropriate configuration from the tabs above to the file

=== ":simple-githubcopilot:{ .middle } &nbsp; GitHub Copilot"

    1. Open GitHub Copilot settings
    2. Navigate to MCP configuration section
    3. Add the appropriate configuration from the tabs above to your MCP settings

</div>

---

## Command Line

Run ToolFront MCP server directly:

```bash
uvx toolfront[postgres] "postgresql://user:pass@host:5432/mydb" --transport stdio
```

!!! tip
    Use `uvx toolfront --help` to see all available command options.