---
icon: lucide/bot
---


# Connect AI agents

Let's connect AI agents to query your app.

## Set up API key

Export your LLM API key:

```console
$ export OPENAI_API_KEY="sk-..."
```

## Command Line

Query your app from the terminal:

```console
$ toolfront ask http://127.0.0.1:8000 "Analyze logs on Feb 3" --model "openai:gpt-5"
```

## Python SDK

Use the Python SDK to query apps from code:

```python
from toolfront import Application

app = Application(url="http://127.0.0.1:8000")

result = app.ask("Analyze logs on Feb 3", model="openai:gpt-5")
```

## MCP server

Connect apps to MCP clients like Claude Code or Cursor:

```json title="claude_desktop_config.json"
{
  "mcpServers": {
    "status-checker": {
      "command": "uvx",
      "args": ["toolfront", "mcp", "http://127.0.0.1:8000"]
    }
  }
}
```
> Aask questions directly through your MCP client

---

!!! success
    You've connected AI agents to your running app.

    **Next:** Explore the [documentation](../../documentation/application/markdown.md) to build more complex RAG apps
