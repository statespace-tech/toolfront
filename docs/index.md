---
icon: lucide/home
---

<p align="center">
  <a href="https://github.com/statespace-tech/toolfront">
    <img src="assets/images/favicon.svg" alt="ToolFront" style="width:20%;">
  </a>
</p>
<div align="center">
    <h1 style="font-weight: 800;"><b>ToolFront</b></h1>
</div>
<p align="center">
    <em>
      Turn your data into shareable RAG apps in minutes. All in pure Markdown. Zero boilerplate.
    </em>
</p>

<p align="center">
  <a href="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml" target="_blank" style="text-decoration: none;">
    <img src="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml/badge.svg" alt="Test Suite">
  </a>
  <a href="https://www.python.org/downloads/" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/badge/python-3.10+-3775A9?style=flat-square" alt="Python 3.10+">
  </a>
  <a href="https://pypi.org/project/toolfront/" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/pypi/v/toolfront?color=3775A9&label=pypi%20package&style=flat-square" alt="PyPI package">
  </a>
  <a href="https://github.com/statespace-tech/toolfront/blob/main/LICENSE" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/badge/license-MIT-007ec6?style=flat-square" alt="License">
  </a>
  <a href="https://discord.gg/rRyM7zkZTf" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&color=5865F2&style=flat-square" alt="Discord">
  </a>
  <a href="https://x.com/statespace_tech" target="_blank" style="text-decoration: none;">
    <img src="https://img.shields.io/badge/Statespace-black?style=flat-square&logo=x&logoColor=white" alt="X">
  </a>
</p>

---

**Source code: [https://github.com/statespace-tech/toolfront](https://github.com/statespace-tech/toolfront)**

---

_ToolFront is a declarative framework for building composable RAG applications in Markdown._

## Simple example

### Create it

Start with one file:`README.md`


```yaml title="README.md"
---
tools:
  - [curl, -X, GET, "https://httpbin.org/status/200"]
---

# Instructions
- Use `curl` to check if the service is up
```

### Serve it

Run your app locally:

```console
$ toolfront serve .
```
> Runs on `http://127.0.0.1:8000`

### Connect it

Connect your app to AI agents:

=== ":simple-python: &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application(url="http://127.0.0.1:8000")

    result = app.ask("Is the service up?", model="openai:gpt-5")
    ```

=== ":lucide-terminal: &nbsp; Command line"

    ```console
    $ toolfront ask http://127.0.0.1:8000 "Is the service up?" --model "openai:gpt-5"
    ```

=== ":simple-modelcontextprotocol: &nbsp; MCP server"

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

Update `README.md` with tools to navigate other files:

```yaml title="README.md" hl_lines="4-5 10"
---
tools:
  - [curl, -X, GET, "https://httpbin.org/status/200"]
  - [ls]
  - [cat]
---

# Instructions
- Use `curl` to check if the service is up
- Use `ls` and `cat` to navigate other files
```

### Compose it

Add pages for different RAG workflows:

=== ":lucide-list-indent-increase: &nbsp; Vector Search"

    ```yaml title="src/vector_search.md"
    ---
    tools:
      - [curl, -X, POST, https://host.pinecone.io/records/namespaces/user/search]
    ---

    # Vector search instructions:
    - Query documents with your vector database API
    ```

=== ":lucide-database: &nbsp; Text-to-SQL"

    ```yaml title="src/text2sql.md"
    ---
    tools:
      - [psql, -U, $USER, -d, $DB, -c, { regex: "^SELECT\b.*" }]
    ---

    # Text-to-SQL instructions:
    - Use `psql` for read-only PostgreSQL queries
    ```

=== ":lucide-bot: &nbsp; Agentic RAG"

    ```yaml title="src/agentic_rag.md"
    ---
    tools:
      - [grep, -r, -i, { }, ../data/]
    ---

    # Document search instructions:
    - Use `grep` to search documents in `../data/`
    ```

### Deploy it

Create a free [Statespace account](#deploy-it)[^1] and deploy your app to the cloud:

```console
$ toolfront deploy .
```
> Accesible at `https://<app-id>.toolfront.app`. Share it with the community or your team!


## Installation

Install `toolfront` with your favorite PyPI package manager:

=== ":fontawesome-brands-python: &nbsp; pip"

    ```console
    $ pip install toolfront
    ```

=== ":simple-uv: &nbsp; uv"

    ```console
    $ uv add toolfront
    ```

=== ":simple-poetry: &nbsp; poetry"

    ```console
    $ poetry add toolfront
    ```

[^1]: Statespace is currently in beta. Email `esteban[at]statespace[dot]com` or join our [Discord](https://discord.gg/rRyM7zkZTf) to get an API key.
