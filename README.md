<p align="center">
  <a href="https://github.com/statespace-ai/toolfront">
    <img src="https://raw.githubusercontent.com/statespace-ai/toolfront/main/docs/assets/img/logo.svg" width="150" alt="ToolFront Logo">
  </a>
</p>

<div align="center">

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

## Installation

Install `toolfront` with `pip` or your favorite PyPI package manager.

```bash
pip install toolfront
```

## Quickstart

ToolFront helps you build and deploy environments for AI agents. Think of environments as interactive directories that agents can explore and take actions in.

```markdown
environment
├── index.md
├── pages/
│   ├── database.md
│   ├── document.md
│   └── api.md
└── data/
    ├── receipt_20240115_001.txt
    └── receipt_20240118_002.txt
```

To add actions to an environment, simply define commands in any markdown header. As agents browse files, they will discover these tools and learn how to use them with the `--help` flag.

```markdown
---
tools:
- [python3, cli.py]
- [curl, -X, GET, https://api.example.com/data]

---

# My environment page

Add [links](./page_1) to tell your agents what pages they should check out.

Agents can call any command defined in markdown headers.
- `python3 cli.py` executes a python script
- `curl -X GET https://api.example.com/data` calls an API
```

You can launch browsing sessions with ToolFront's Python SDK, or build your own browsing agent with the MCP. Browsing is always powered by your own models.

### Using the SDK

```python
from toolfront import Browser

browser = Browser(model="openai:gpt-5")

url = "file:///path/to/environment"

answer = browser.ask("What's our average ticket price?", url=url)
print(answer)
```

### Using MCP

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

ToolFront's comes with six core tools your agents can use to interact with environments:

- **`run_command`** - Execute commands defined in markdown headers
- **`read`** - Get the content of a specific page or file
- **`glob`** - List files matching a pattern
- **`tree`** - View directory structure
- **`search`** - Find relevant documents or lines[^1]

[^1]: `search` requires indexing environment files.

## ToolFront Cloud

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