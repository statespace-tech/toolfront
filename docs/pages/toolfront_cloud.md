# ToolFront Cloud

ToolFront Cloud serves your environments over the web, making them accessible from anywhere.

---

## Benefits

Cloud deployment offers several advantages over local environments or self-hosting.

- **Separation of Concerns** - Scale and deploy agents and environments independently
- **Remote Access** - Access environments from anywhere with a single URL
- **Automatic Indexing** - Get instant BM25 semantic search on deployment
- **Zero Infrastructure** - No server setup, SSL certificates, or maintenance
- **Built-in Security** - API key authentication and HTTPS included

---

## Usage

Deploy your environment:

```bash
toolfront deploy ./path/environment
```

Connect agents using the secure URL with the **[Python SDK](./python_sdk.md)** or **[MCP Server](./mcp_server.md)**:

=== ":simple-python:{ .middle } &nbsp; Python SDK"

    ```python
    from toolfront import Environment

    environment = Environment(
        url="https://cloud.toolfront.ai/user/environment",
        params={"API_KEY": "your-api-key"}
    )

    result = environment.run("What's our best-seller?", model="openai:gpt-5")
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
            "https://cloud.toolfront.ai/user/environment",
            "--param",
            "API_KEY=your-api-key"
          ]
        }
      }
    }
    ```

Cloud environments are indexed with BM25 and get access to the `search` tool:

```
Let me search for documents relevant to "ticket pricing API"...

Found 3 relevant pages:
  - ./api/pricing.md (highly relevant)
  - ./guides/analytics.md (relevant)
  - ./examples/queries.md (somewhat relevant)

I'll start by reading ./api/pricing.md...
```

---

!!! toolfront "Beta access"
    To get access to our beta, join our **[Discord](https://discord.gg/rRyM7zkZTf)** or email `esteban[at]kruskal[dot]ai`.
