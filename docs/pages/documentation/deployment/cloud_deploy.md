---
icon: lucide/cloud-upload
---

# Cloud deployment

Deploy and manage your ToolFront applications with simple commands.


!!! info "First time?"
    Create a free [Statespace account](https://statespace.com/signup) to get your API key.


## Quick deploy

### Public apps

Share your apps with the community.

```bash
toolfront deploy . --public
```

> Deploys to `https://<app-id>.toolfront.app`


### Private apps

Deploy private apps with authentication.

```bash
toolfront deploy . --private
```
> Deploys to `https://<app-id>.toolfront.app` with authentication token


## Usage

Once deployed, connect to your app from anywhere.

=== ":simple-python: &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application(
        "https://<app-id>.toolfront.app",
        param={"Authorization": "Bearer YOUR_TOKEN"} # (1)!
    )
    result = app.ask("Your question", model="openai:gpt-5")
    ```

    1. Authorization is only required for private apps

=== ":simple-modelcontextprotocol: &nbsp; MCP Server"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront", "mcp", "https://<app-id>.toolfront.app",
            "--param", "Authorization=Bearer YOUR_TOKEN" // (1)!
          ]
        }
      }
    }
    ```

    1. Authorization is only required for private apps

=== ":lucide-terminal: &nbsp; Command Line"

    ```bash
    toolfront ask https://<app-id>.toolfront.app "Your question" \
      --param "Authorization=Bearer YOUR_TOKEN"  # (1)!
    ```

    1. Authorization is only required for private apps

!!! question "Learn more"
    Check out the [Python SDK](../integration/python_sdk.md), [MCP Server](../integration/mcp_server.md), [Command Line](../integration/command_line.md), and [REST API](../integration/rest_api.md) documentation for more details.


## Deployment options

| Feature | Community Cloud | Statespace Cloud | Enterprise |
|---------|----------------|------------------|------------|
| **Pricing** | Free | $39/month | Custom |
| **Public Apps** | 5 | 20 | Unlimited |
| **Private Apps** | :x: | 20 | Unlimited |
| **Team Collaboration** | :x: | :white_check_mark: | :white_check_mark: |
| **Support** | Community | Priority | Dedicated |

**Community Cloud** - Perfect for getting started with public apps. Free forever.

**Statespace Cloud** - For teams and private apps with authentication. [Learn more](https://statespace.com/)

**Enterprise** - Custom deployment with unlimited apps and dedicated support. [Contact us](https://statespace.com)


## Management

### List apps

View all your deployed applications.

```bash
toolfront list [OPTIONS]
```

### Update an app

Update an existing deployment with new files.

```bash
toolfront update [OPTIONS] DEPLOYMENT_ID PATH
```


### Delete an app

Remove a deployment from the cloud.

```bash
toolfront delete [OPTIONS] DEPLOYMENT_ID
```

!!! question "Learn more"
    See the [CLI Commands documentation](../../reference/client_library/cli_commands.md) for complete command syntax and options.