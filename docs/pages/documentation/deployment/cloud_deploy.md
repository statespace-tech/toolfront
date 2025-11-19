---
icon: lucide/cloud-upload
---

# Cloud Deployment

Deploy and manage your ToolFront applications with simple commands.

## Quick Deploy

### Public Apps

Share your apps with the community.

```bash
toolfront deploy . --public
# Deployed to: https://<app-id>.toolfront.app
```

### Private Apps

Deploy private apps with authentication.

```bash
toolfront deploy . --private
# Deployed to: https://<app-id>.toolfront.app
# Authentication token: YOUR_TOKEN
```

!!! info "First time?"
    Create a free [Statespace account](https://statespace.com/signup) to start deploying apps.

## Usage

Once deployed, connect to your app from anywhere.

### Public Apps

=== ":simple-python: &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application("https://<app-id>.toolfront.app")
    result = app.ask("Your question", model="openai:gpt-5")
    ```

=== ":simple-modelcontextprotocol: &nbsp; MCP Server"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", "https://<app-id>.toolfront.app"]
        }
      }
    }
    ```

=== ":lucide-terminal: &nbsp; Command Line"

    ```bash
    toolfront ask https://<app-id>.toolfront.app "Your question"
    ```

### Private Apps

=== ":simple-python: &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application(
        "https://<app-id>.toolfront.app",
        param={"Authorization": "Bearer YOUR_TOKEN"}
    )
    result = app.ask("Your question", model="openai:gpt-5")
    ```

=== ":simple-modelcontextprotocol: &nbsp; MCP Server"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront", "mcp", "https://<app-id>.toolfront.app",
            "--header", "Authorization: Bearer YOUR_TOKEN"
          ]
        }
      }
    }
    ```

=== ":lucide-terminal: &nbsp; Command Line"

    ```bash
    toolfront ask https://<app-id>.toolfront.app "Your question" \
      --header "Authorization: Bearer YOUR_TOKEN"
    ```

!!! question "Learn more"
    See [Python SDK](../integration/python_sdk.md), [MCP Server](../integration/mcp_server.md), [Command Line](../integration/command_line.md), and [REST API](../integration/rest_api.md) for more details.


## Deployment Options

| Feature | Community Cloud | Statespace Cloud | Enterprise |
|---------|----------------|------------------|------------|
| **Pricing** | Free | $39/month | Custom |
| **Public Apps** | 5 | Unlimited | Unlimited |
| **Private Apps** | :x: | 20 | Unlimited |
| **Team Collaboration** | :x: | :white_check_mark: | :white_check_mark: |
| **Support** | Community | Priority | Dedicated |

**Community Cloud** - Perfect for getting started with public apps. Free forever.

**Statespace Cloud** - For teams and private apps with authentication. [Learn more](https://statespace.app/pricing)

**Enterprise** - Custom deployment with unlimited apps and dedicated support. [Contact us](https://statespace.app/contact)


## Management

### List Apps

View all your deployed applications.

```bash
toolfront list [OPTIONS]
```

### Update an App

Update an existing deployment with new files.

```bash
toolfront update [OPTIONS] DEPLOYMENT_ID PATH
```


### Delete an App

Remove a deployment from the cloud.

```bash
toolfront delete [OPTIONS] DEPLOYMENT_ID
```

!!! question "Learn more"
    See the [CLI Commands](../../reference/client_library/cli_commands/) reference for full documentation.
