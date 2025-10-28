# ToolFront Cloud

ToolFront Cloud serves your applications over the web, making them accessible from anywhere.

---

## Benefits

Cloud deployment offers several advantages over local applications or self-hosting.

- **Separation of Concerns** - Scale and deploy agents and applications independently
- **Remote Access** - Access applications from anywhere with a single URL
- **Automatic Indexing** - Get instant BM25 semantic search on deployment
- **Zero Infrastructure** - No server setup, SSL certificates, or maintenance
- **Built-in Security** - API key authentication and HTTPS included

---

## Usage

Deploy your application:

```bash
toolfront deploy ./path/to/project
```

Connect agents using the secure URL with the Python SDK or MCP Server:

=== ":simple-python:{ .middle } &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application(
        url="https://cloud.toolfront.ai/user/project",
        params={"API_KEY": "your-api-key"}
    )

    result = app.run("What's our best-seller?", model="openai:gpt-5")
    ```

=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP Server"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront",
            "mcp",
            "https://cloud.toolfront.ai/user/project",
            "--param",
            "API_KEY=your-api-key"
          ]
        }
      }
    }
    ```

---

!!! toolfront "Beta access"
    To get access to our beta, join our **[Discord](https://discord.gg/rRyM7zkZTf)** or email `esteban[at]kruskal[dot]ai`.
