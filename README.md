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

ToolFront is a declarative framework for building modular AI applications in Markdown. Write tools and instructions in `.md` files and get a live AI application.

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

### Ask it

Export your `OPENAI_API_KEY` and query your app:

<details open>
<summary><b>Python SDK</b></summary>

```python
from toolfront import Application

app = Application(url="http://127.0.0.1:8000")

result = app.ask("Is the service up?", model="openai:gpt-5")
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

<details>
<summary><b>Command Line</b></summary>

```bash
toolfront ask http://127.0.0.1:8000 "Is the service up?"
```

</details>

## Upgraded Example

Your app can grow into a full project:

```bash
project/
├── README.md          # Main instructions & navigation tools
├── src/
│   ├── rag.md         # Document search
│   ├── text2sql.md    # Database query
│   └── toolkit.md     # Custom workflow
├── data/
└── tools/

4 directories, 10 files
```

### Add Navigation Tools

Update `README.md` with tools to explore the project.

```yaml
---
tools:
  - [curl, -X, GET, "https://httpbin.org/status/200"]
  - [ls]
  - [cat]
---

# Instructions
- Use `curl` to check if the service is up
- Use `ls` and `cat` to browse other files
```

### Add Specialized Tools

Expand your app with specialized workflows.

<details open>
<summary><b>Document Search</b></summary>

```yaml
---
tools:
  - [grep]
---

# Document Search
- Use `grep` for keyword searches in `data/`.
```

</details>

<details>
<summary><b>Text-to-SQL</b></summary>

```yaml
---
tools:
  - [psql, -U, $USER, -d, $DB, -c, { regex: "^SELECT\b.*" }]
---

# Database Access
- Call `psql` to query the database with read-only SELECT statements
```

</details>

<details>
<summary><b>Custom Scripts</b></summary>

```yaml
---
tools:
  - [python3, tools/analyze.py]
---

# Custom Tools
- Run `analyze.py` to process data, passing `--input` as needed
```

</details>

### Deploy It

Create a free [Statespace account](#deploy-it)[^1] and deploy your app in one command.

```bash
toolfront deploy .
```

> Deploys to `https://your-app.toolfront.app`. Share it with the community or your team!

## Installation

Install `toolfront` with your favorite PyPI package manager (Requires Python 3.10+).

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

[^1]: Statespace is currently in beta. Email `esteban[at]statespace[dot]com` or join our [Discord](https://discord.gg/rRyM7zkZTf) to get an API key