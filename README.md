<p align="center">
  <a href="https://github.com/statespace-ai/toolfront">
    <img src="https://raw.githubusercontent.com/statespace-ai/toolfront/main/docs/assets/images/logo.png" width="150" alt="ToolFront Logo">
  </a>
</p>

<div align="center">

# ToolFront

*Data environments for AI agents*

[![Test Suite](https://github.com/statespace-ai/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/statespace-ai/toolfront/actions/workflows/test.yml)
[![PyPI package](https://img.shields.io/pypi/v/toolfront?color=%2334D058&label=pypi%20package)](https://pypi.org/project/toolfront/)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square)](https://discord.gg/rRyM7zkZTf)
[![X](https://img.shields.io/badge/ToolFront-black?style=flat-square&logo=x&logoColor=white)](https://x.com/statespace_ai)

</div>

---

**Documentation: [docs.toolfront.ai](http://docs.toolfront.ai/)**

**Source code: [https://github.com/statespace-ai/toolfront](https://github.com/statespace-ai/toolfront)**

---

ToolFront helps you build and deploy environments for AI agents. Think of environments as interactive directories that agents can explore and take actions in.

```bash
environment/
├── index.md
├── pages/
│   ├── text2sql.md
│   ├── document.md
│   └── api.md
├── tools/
│   └─ extract.py
└── data/
    ├── invoices/
    └── logs/
```

Agents can run commands listed in markdown headers. As they browse files, they will discover these tools and learn how to use them with the `--help` flag.

**Landing Page**

```markdown
# index.md

---
tools:
  - [date, +%Y-%m-%d]
---

# Landing Page

Add instructions and tools to markdown pages.
- Agents can only run commands in headers
- Links to [pages](./pages) help with navigation
```

<details>
<summary><b>Text-to-SQL</b></summary>

```markdown
# text2sql.md

---
tools:
  - [toolfront, database, $POSTGRES_URL]
---

# Text-to-SQL

Build text-to-SQL workflows with the `toolfront database` CLI.
- Agents may run `list-tables`, `inspect-table`, and `query` subcommands
- All queries are restricted to read-only operations
```

</details>

<details>
<summary><b>Document RAG</b></summary>

```markdown
# document.md

---
tools:
  - [python, tools/extract.py]
---

# Document RAG

Link to [directories](./data) where documents are stored.
- Agents use built-in tools like `read`, `glob`, and `grep` to search files
- Custom tools can be added for data extraction and processing
```

</details>

<details>
<summary><b>API Integration</b></summary>

```markdown
# api.md

---
tools:
  - [curl, -X, GET, "https://api.products.com/v1/pricing"]
---

# API Integration

Define API endpoints as executable tools using `curl` commands.
- Agents can call external APIs to fetch live data
- Include environment `$VARIABLES` for authentication
```

</details>

You can launch browsing sessions with ToolFront's Python SDK, or build your own browsing agent with the MCP. Browsing is always powered by your own models.

**SDK**

```python
from toolfront import Browser

browser = Browser(model="openai:gpt-5")

url = "file:///path/to/environment"

answer = browser.ask("What's our average ticket price?", url=url)
print(answer)
```

<details>
<summary><b>MCP</b></summary>

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": ["toolfront", "mcp", "file:///path/to/toolsite"]
    }
  }
}
```

</details>

ToolFront comes with six core tools your agents can use to interact with environments:

- **`run_command`** - Execute commands defined in markdown headers
- **`read`** - Read the content of a specific file
- **`tree`** - View directory structure
- **`glob`** - List files matching a glob pattern
- **`grep`** - Search files using regex patterns
- **`search`** - Find relevant documents using BM25 full-text search*

*`search` requires indexing environment files.

## Installation

To get started, install `toolfront` using your favorite PyPI package manager.

```bash
pip install toolfront
```


## Deploy with ToolFront Cloud

Instantly deploy your environments with **ToolFront Cloud**.

```bash
toolfront deploy ./path/to/environment --api-key "my-api-key"
```

Would give you a secure environment URL your agents can browse.

```python
answer = browser.ask(..., url="https://cloud.toolfront.ai/user/environment")
```

Environments deployed with **ToolFront Cloud** are automatically indexed and get access to the powerful `search` tool.

```
Let me search the environment for documents relevant to "ticket pricing API"...

Found 3 relevant pages:
  - ./api/pricing.md (highly relevant)
  - ./guides/analytics.md (relevant)
  - ./examples/queries.md (somewhat relevant)

I'll start by reading ./api/pricing.md...
```

**ToolFront Cloud** is currently in open beta. To request access, join our [Discord](https://discord.gg/rRyM7zkZTf) or email `esteban[at]kruskal[dot]ai`.


## Community & Contributing

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **X**: Follow us [@toolfront](https://x.com/toolfront) for updates and news
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/statespace-ai/toolfront/issues)

## License

This project is licensed under the terms of the MIT license.