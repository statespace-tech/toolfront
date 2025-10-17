<p align="center">
  <a href="https://github.com/statespace-tech/toolfront">
    <img src="https://raw.githubusercontent.com/statespace-tech/toolfront/main/docs/assets/images/logo.png" width="150" alt="ToolFront Logo">
  </a>
</p>

<div align="center">

# ToolFront

*Data environments for AI agents*

[![Test Suite](https://github.com/statespace-tech/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/statespace-tech/toolfront/actions/workflows/test.yml)
[![PyPI package](https://img.shields.io/pypi/v/toolfront?color=%2334D058&label=pypi%20package)](https://pypi.org/project/toolfront/)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square)](https://discord.gg/rRyM7zkZTf)
[![X](https://img.shields.io/badge/Statespace-black?style=flat-square&logo=x&logoColor=white)](https://x.com/statespace_tech)

</div>

---

**Documentation: [docs.toolfront.ai](http://docs.toolfront.ai/)**

**Source code: [https://github.com/statespace-tech/toolfront](https://github.com/statespace-tech/toolfront)**

---

## Installation

Install `toolfront` with your favorite PyPI package manager.

```bash
pip install toolfront
```

## Quickstart

ToolFront helps you organize AI workflows into independent tasks with **environments**.

```bash
environment/
├── index.md
├── pages/
│   ├── text2sql.md
│   ├── document.md
│   └── api.md
└── data/
    ├── invoices/
    └── logs/

5 directories, 15 files
```

<details open>
<summary><b>Landing Page</b></summary>

Declare task instructions and tools in Markdown files.

```markdown
---
tools:
  - [date, +%Y-%m-%d]

---

# Landing Page

- Include links to [pages](./pages)
- Add tool commands to frontmatters
- Agents learn tools with `--help`
```

</details>

<details>
<summary><b>Text-to-SQL</b></summary>

Create text-to-SQL tasks with ToolFront's built-in [database CLI](https://docs.toolfront.ai/pages/database_cli/).

```markdown
---
tools:
  - [toolfront, database, $DB_URL]

---

# Text-to-SQL

- Add database metadata and context
- Agents can list and inspect tables
- All queries are read-only
```

</details>

<details>
<summary><b>Document RAG</b></summary>

Retrieve information from data files like `.txt`, `.csv`, and `.json`.

```markdown
---
tools:
  - [python, extract.py]

---

# Document RAG

- Add data files and descriptions
- Agents read and search documents
- Use custom tools to process data
```

</details>

<details>
<summary><b>API Integration</b></summary>

Fetch live data with calls to external APIs.

```markdown
---
tools:
  - [curl, "https://api.com/v1/user"]

---

# API Integration

- Define API endpoints as tools
- Pass env `$VARS` for secrets
- Agents fetch live external data
```

</details>

Agents browse environments to get work done, using tools and following instructions as needed.

<details open>
<summary><b>Python SDK</b></summary>

Run Python agents on environments with the [SDK](https://docs.toolfront.ai/pages/python_sdk/).

```python
from toolfront import Environment

env = Environment(url="file:///path/environment")

response = env.run("What's our average ticket size?", model="openai:gpt-5")
```

</details>

<details>
<summary><b>MCP Server</b></summary>

Connect your own agents to environments with the [MCP Server](https://docs.toolfront.ai/pages/mcp_server/).

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": ["toolfront", "mcp", "file:///path/environment"]
    }
  }
}
```

</details>

## Deploy with ToolFront Cloud

Instantly deploy your environments with [ToolFront Cloud](https://docs.toolfront.ai/pages/toolfront_cloud/).

```bash
toolfront deploy ./path/environment
```

This gives you a secure environment URL your agents can access from anywhere.

```python
Environment(url="https://cloud.toolfront.ai/user/environment", params={"API_KEY": ...})
```

ToolFront Cloud is in beta. To request access, join our [Discord](https://discord.gg/rRyM7zkZTf) or email `esteban[at]kruskal[dot]ai`.


## Community & Contributing

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **X**: Follow us [@toolfront](https://x.com/toolfront) for updates and news
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/statespace-tech/toolfront/issues)

## License

This project is licensed under the terms of the MIT license.