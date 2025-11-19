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
      Build and deploy AI apps in minutes. All in pure Markdown. Zero boilerplate.
    </em>
</p>

<p align="center">
  <a href="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml" target="_blank" style="text-decoration: none;">
    <img src="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml/badge.svg" alt="Test Suite">
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

ToolFront is a declarative framework for building modular AI applications in Markdown. Write tools and instructions in `.md` files and get a live AI application.

## Simple Example

### Create it

  Start with one file: `README.md`


  ```markdown title="README.md"
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
# Running on http://127.0.0.1:8000
```

### Ask it

Export your `OPENAI_API_KEY` and query your app:

=== ":simple-python: &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application(url="http://127.0.0.1:8000")

    result = app.ask("Is the service up?", model="openai:gpt-5")
    ```

=== ":simple-modelcontextprotocol: &nbsp; MCP Server"

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
  
=== ":lucide-terminal: &nbsp; Command Line"

    ```bash
    toolfront ask http://127.0.0.1:8000 "Is the service up?"
    ```

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

  ```markdown title="README.md" hl_lines="4-5 11"
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

=== ":lucide-folder-search: &nbsp; Document Search"

      ```markdown title="src/rag.md"
      ---
      tools:
        - [grep]

      ---

      # Document Search
      - Use `grep` for keyword searches in `data/`.
      ```

=== ":lucide-database: &nbsp; Text-to-SQL"

    ```markdown title="src/text2sql.md"
    ---
    tools:
      - [psql, -U, $USER, -d, $DB, -c, {{ "^SELECT\b.*" }}]

    ---

    # Database Access
    - Call `psql` to query the database with read-only SELECT statements
    ```

=== ":lucide-file-code: &nbsp; Custom Scripts"

    ```markdown title="src/toolkit.md"
    ---
    tools:
      - [python3, tools/analyze.py"]

    ---
    
    # Custom Tools
    - Run `analyze.py` to process data, passing `--input` as needed
    ```

### Deploy It

Deploy your app in one command.

```bash
toolfront deploy .
# Deployed to: https://your-app.toolfront.app
```

Then, share it with the community or your team.

=== ":material-web: Community Cloud (Free)"

    ```python
    # Up to 5 public apps, totally free
    app = Application("https://fte499.toolfront.app")
    ```

=== ":material-account-group: Statespace Cloud (Pro)"

    ```python
    # Up to 20 public or private apps with authentication
    app = Application("https://fte499.toolfront.app", param={"Authorization": ...})
    ```

=== ":material-lock: Self-Hosted (Enterprise)"

    ```python
    # Unlimited on-prem apps with Docker or K8s
    app = Application("https://fte499.toolfront.app", param={"Authorization": ...})
    ```


## Installation

Install `toolfront` with your favorite PyPI package manager[^1].

=== ":fontawesome-brands-python: &nbsp; pip"

    ```bash
    pip install toolfront
    ```

=== ":simple-uv: &nbsp; uv"

    ```bash
    uv add toolfront
    ```

=== ":simple-poetry: &nbsp; poetry"

    ```bash
    poetry add toolfront
    ```

[^1]: Requires Python 3.10+