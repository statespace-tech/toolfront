---
icon: lucide/bot
---


# Connect AI Agents

Your status checker app is deployed. Now, let's connect OpenAI's GPT-5 to interact with with it.

## Set Up API Key

Export your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
```

## Command Line

Query your app from the terminal:

```bash
toolfront ask http://127.0.0.1:8000 "What's the current service status?" \ 
  --model "openai:gpt-5"

toolfront ask http://127.0.0.1:8000 "Search logs for errors on Feb 3" \
  --model "openai:gpt-5"
```


## Python SDK

Use the Python SDK to integrate apps with your code.

```python
from toolfront import Application

app = Application(url="http://127.0.0.1:8000")

# Check current status
result = app.ask("What's the current service status?", model="openai:gpt-5")

# Search historical logs
result = app.ask("Find errors in the logs", model="openai:gpt-5")
```

## MCP Server

Connect Claude Desktop or other MCP clients.

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

---

!!! success
    You've connected AI agents to your running app.

    **Next:** Explore the [documentation](../../documentation/application/markdown.md) to build more complex apps