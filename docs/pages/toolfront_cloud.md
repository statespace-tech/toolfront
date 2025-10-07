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

To request beta access, join our [Discord server](https://discord.gg/rRyM7zkZTf) or  email  **esteban [at] kruskal [dot] ai**.