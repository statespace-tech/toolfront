<p align="center">
  <a href="https://github.com/statespace-tech/toolfront">
    <img src="https://raw.githubusercontent.com/statespace-tech/toolfront/main/docs/assets/images/favicon.svg" width="150" alt="ToolFront">
  </a>
</p>

<div align="center">

# ToolFront

**Build and deploy AI apps in minutes. All in pure Markdown. Zero boilerplate.**

[![Test Suite](https://github.com/statespace-tech/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/statespace-tech/toolfront/actions/workflows/test.yml)
[![PyPI package](https://img.shields.io/pypi/v/toolfront?color=%2334D058&label=pypi%20package)](https://pypi.org/project/toolfront/)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square)](https://discord.gg/rRyM7zkZTf)
[![X](https://img.shields.io/badge/Statespace-black?style=flat-square&logo=x&logoColor=white)](https://x.com/statespace_tech)

</div>

---

**Documentation: [docs.toolfront.ai](http://docs.toolfront.ai/)**

**Source code: [https://github.com/statespace-tech/toolfront](https://github.com/statespace-tech/toolfront)**

---

## Quickstart

ToolFront is a declarative framework for building modular AI applications in Markdown. Write tools and instructions in `.md` files, run the project, and get a live AI application.

### Create it

Start with **one file**: `README.md`

```markdown
---
tools:
  - [curl, -X, GET, "https://httpbin.org/status/200"]
---

# Status Checker
- Use `curl` to check if the service is up
```

### Run it

Run the application with:

```bash
toolfront run .
```

### Ask it

Ask your AI application.

<details open>
<summary><b>Python SDK</b></summary>

```python
from toolfront import Application

app = Application(url="http://127.0.0.1:8000")

result = app.ask("Is the service up?", model="openai:gpt-5")

print(result)
# Answer: yes
```

</details>

<details>
<summary><b>MCP Server</b></summary>

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": ["toolfront", "mcp", "http://127.0.0.1:8000"]
    }
  }
}
```

</details>

---

## Upgraded Example

Your full project can grow like this:

```bash
project/
├── README.md
├── src/
│   ├── api.md
│   ├── rag.md
│   ├── text2sql.md
│   └── toolkit.md
├── data/
└── tools/
```

### Add Navigation

Update `README.md` with tools to explore the project

```markdown
---
tools:
  - [curl, -X, GET, "https://httpbin.org/status/200"]
  - [ls]
  - [cat]
---

# Status Checker
- Use `curl` to check if the service is up
- Use `ls` and `cat` to browse other files
```

### Add Document RAG

Give your agent tools to search documents

```markdown
---
tools:
  - [grep]
---

# Search Docs
- Use `grep` to search files in `/data/`
```

### Add Text-to-SQL

Connect your databases for SQL workflows

```markdown
---
tools:
  - [psql, -U, $USER, -d, $DATABASE, -c, {query}]
---

# Database Access
- Call the `psql` tool to query the PostgreSQL database
```

### Add Custom Tools

Build custom tools in any programming language

```markdown
---
tools:
  - [python, tools/status.py, --delayed]
---

# Custom Tools
- Run `status.py` to check delayed orders
```

---

## Installation

Install `toolfront` with your favorite PyPI package manager.

<details open>
<summary><b>pip</b></summary>

```bash
pip install toolfront
```

</details>

<details>
<summary><b>uv</b></summary>

```bash
uv add toolfront
```

</details>

<details>
<summary><b>poetry</b></summary>

```bash
poetry add toolfront
```

</details>

---

## Deploy your Apps

Instantly deploy your AI applications:

```bash
toolfront deploy ./path/to/project
```

Gives you a shareable application URL:

<details open>
<summary><b>Community Cloud (Free)</b></summary>

```python
# Up to 5 public apps, totally free
app = Application("https://cloud.statespace.com/you/status-checker")
```

</details>

<details>
<summary><b>Statespace Cloud (Pro)</b></summary>

```python
# Up to 20 public or private apps with authentication
app = Application("https://cloud.statespace.com/team/project", params={"API_KEY": "..."})
```

</details>

<details>
<summary><b>Self-Hosted (Enterprise)</b></summary>

```python
# Unlimited on-prem apps with Docker or K8s
app = Application("https://custom.com/agent")
```

</details>

[Get started for free](https://cloud.statespace.com/signup)


## Community & Contributing

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **X**: Follow us [@toolfront](https://x.com/toolfront) for updates and news
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/statespace-tech/toolfront/issues)

## License

This project is licensed under the terms of the MIT license.