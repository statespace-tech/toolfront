---
icon: lucide/cloud-upload
---

# Cloud deployment

Deploy and manage your RAG applications with simple commands.


!!! info "First time?"
    Create a free [Statespace account](https://statespace.com/signup) to get your API key.


## Quick deploy

Deploy your application as public (community access) or private (authenticated access).

**Public deployment:**
```bash
toolfront deploy ./project --public
```
> Accessible at `https://<app-id>.toolfront.app` (anyone can use)

**Private deployment:**
```bash
toolfront deploy ./project --private
```
> Accessible at `https://<app-id>.toolfront.app` (requires authentication)


## Usage

Once deployed, connect AI agents to your app.

=== ":simple-python: &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application(
            url="https://<app-id>.toolfront.app",
            headers={"Authorization": "Bearer YOUR_TOKEN"}
    )

    result = app.ask("Who are our top-3 customers?", model="openai:gpt-5")
    ```


=== ":simple-modelcontextprotocol: &nbsp; MCP Server"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront", "mcp", "https://<app-id>.toolfront.app",
            "--param", "Authorization=Bearer YOUR_TOKEN"
          ]
        }
      }
    }
    ```

=== ":lucide-terminal: &nbsp; Command Line"

    ```console
    $ toolfront ask https://<app-id>.toolfront.app \
        "Who are our top-3 customers?" \
        --param "Authorization=Bearer YOUR_TOKEN" \
        --model "openai:gpt-5"
    ```
> Only private apps require authentication via `Authorization` header

!!! question "Learn more"
    Check out the [Python SDK](../integration/python_sdk.md), [MCP server](../integration/mcp_server.md), and [command Line](../integration/command_line.md) documentation for more details.

## Management

### List apps

View all deployed applications:

```bash
toolfront list
```

### Update an app

Push changes to an existing deployment:

```bash
toolfront update <app-id> ./project
```

### Delete an app

Permanently remove a deployment:

```bash
toolfront delete <app-id>
```

!!! question "Learn more"
    See the [CLI reference](../../reference/client_library/cli_commands.md#toolfront-tokens) for more details on app deployment commands.