<p align="center">
  <a href="https://github.com/statespace-tech/toolfront">
    <img src="https://raw.githubusercontent.com/statespace-tech/toolfront/main/docs/assets/images/favicon.svg" width="150" alt="ToolFront">
  </a>
</p>

<div align="center">

# ToolFront

**Turn your data into shareable RAG apps in minutes. All in pure Markdown. Zero boilerplate.**

[![Test Suite](https://github.com/statespace-tech/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/statespace-tech/toolfront/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3775A9?style=flat-square)](https://www.python.org/downloads/)
[![PyPI package](https://img.shields.io/pypi/v/toolfront?color=3775A9&label=pypi%20package&style=flat-square)](https://pypi.org/project/toolfront/)
[![License](https://img.shields.io/badge/license-MIT-007ec6?style=flat-square)](https://github.com/statespace-tech/toolfront/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&color=5865F2&style=flat-square)](https://discord.gg/rRyM7zkZTf)
[![X](https://img.shields.io/badge/Statespace-black?style=flat-square&logo=x&logoColor=white)](https://x.com/statespace_tech)

</div>

---

**Documentation: [docs.toolfront.ai](http://docs.toolfront.ai/)**

**Source code: [https://github.com/statespace-tech/toolfront](https://github.com/statespace-tech/toolfront)**

---

## Simple example

ToolFront is a declarative framework for building composable RAG applications in Markdown.

### Create it

Start with one file: `README.md`

```yaml
---
tools:
  - [curl, -X, GET, "https://httpbin.org/status/200"]
---

# Instructions
- Use `curl` to check if the service is up
```

### Serve it

Run your app on your machine:

```bash
toolfront serve .
```

> Runs at `http://127.0.0.1:8000`

### Connect it

Connect your app to AI agents:

<details open>
<summary><b>Python SDK</b></summary>

```python
from toolfront import Application

app = Application(url="http://127.0.0.1:8000")

result = app.ask("Is the service up?", model="openai:gpt-5")
```

</details>

<details>
<summary><b>Command line</b></summary>

```bash
toolfront ask http://127.0.0.1:8000 "Is the service up?" --model "openai:gpt-5"
```

</details>

<details>
<summary><b>MCP server</b></summary>

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

## Complex example

### Upgrade it

Your app can grow into a full project:

```bash
project/
├── README.md
├── data/
│   ├── log1.txt
│   ├── log2.txt
│   └── log3.txt
└── src/
    ├── agentic_rag.md
    ├── text2sql.md
    └── vector_search.md

3 directories, 9 files
```

Update `README.md` with CLI tools to progressively discover and read other files:

```yaml
---
tools:
  - [date]
  - [ls]
  - [cat]
---

# Instructions
- Run `date` to check today's date
- Use `ls` and `cat` to discover and read other files
```

### Compose it

Add pages and CLI tools for different workflows:

<details open>
<summary><b>Vector Search</b></summary>

```yaml
---
tools:
  - [curl, -X, POST, https://host.pinecone.io/records/namespaces/user/search]
---

# Vector search instructions:
- Query documents with your vector database API
```

> **Note**: replace the API with your own (e.g., Pinecone, Weaviate, Qdrant)

</details>

<details>
<summary><b>Text-to-SQL</b></summary>

```yaml
---
tools:
  - [psql, -U, $USER, -d, $DB, -c, { regex: "^SELECT\b.*" }]
---

# Text-to-SQL instructions:
- Use `psql` for read-only PostgreSQL queries
```

> **Note**: use your own database CLI (e.g., `mysql`, `sqlite3`, `mongosh`).

</details>

<details>
<summary><b>Agentic RAG</b></summary>

```yaml
---
tools:
  - [grep, -r, -i, { }, ../data/]
---

# Document search instructions:
- Use `grep` to search documents in `../data/`
```

> **Note**: apps can include any file type (e.g. `.csv`, `.sqlite`, `.json`)

</details>

### Deploy it

Create a free [Statespace account](https://statespace.com/) to deploy authenticated private apps:

```bash
toolfront deploy . --private
```

Alternatively, share public apps with the community:

```bash
toolfront deploy . --public
```

> **Note** Statespace gives you app URLs you can paste in prompts and instructions.

## Installation

Install `toolfront` with your favorite PyPI package manager:

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

## Community & Contributing

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **X**: Follow us [@statespace_tech](https://x.com/statespace_tech) for updates and news
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/statespace-tech/toolfront/issues)

## License

This project is licensed under the terms of the MIT license.