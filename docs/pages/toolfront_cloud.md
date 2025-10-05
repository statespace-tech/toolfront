# ToolFront Cloud

Deploy your environments with a single command and get secure, hosted environments your agents can use immediately.

## Quickstart

Deploy your environment:

```bash
toolfront deploy ./path/to/environment --name "my_env"
```

Use it in your agent code:

```python
from toolfront import Browser

browser = Browser(params={"api_key": "TOOLFRONT-API-KEY"})

url = "https://cloud.toolfront.ai/user/my_env"

result = browser.ask("What's our average ticket price?", url=url)
```

---

## Powerful Search

ToolFront Cloud automatically indexes your environment, giving agents the ability to search across pages faster and more accurately. This is especially useful for large environments with many pages.

```
I need to find information about ticket pricing APIs.
Let me search the environment for "ticket pricing API"...

Found 3 relevant pages:
  - ./api/pricing.md (highly relevant)
  - ./guides/analytics.md (relevant)
  - ./examples/queries.md (somewhat relevant)

I'll start by reading ./api/pricing.md
```

To request beta access, please email email **esteban [at] kruskal [dot] ai**

---

## Available Tools

Agents interact with environments using these core tools:

- `search()` - Find relevant pages using BM25 or regex patterns
- `read()` - Get the content of a specific page or file
- `glob()` - List files matching a pattern
- `run_command()` - Execute commands defined in page frontmatter

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                          Browser                             │
│                                                              │
│  ┌──────────────┐       ┌──────────────┐                    │
│  │ AI Agent/LLM │  ───> │  MCP Tools   │                    │
│  └──────────────┘       └──────────────┘                    │
│                               │                              │
└───────────────────────────────┼──────────────────────────────┘
                                │
                                │ search()
                                │ read()
                                │ glob()
                                │ run_command()
                                ▼
                         ┌──────────────┐
                         │ Environment  │
                         └──────────────┘
```
