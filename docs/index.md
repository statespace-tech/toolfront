---
icon: material/lightning-bolt
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
    <em>Build and deploy AI apps in minutes. All in pure Markdown. Zero boilerplate.
</em>
</em>
</p>

<p align="center">
<a href="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml" target="_blank">
    <img src="https://github.com/statespace-tech/toolfront/actions/workflows/test.yml/badge.svg" alt="Test Suite">
</a>
<a href="https://pypi.org/project/toolfront/" target="_blank">
    <img src="https://img.shields.io/pypi/v/toolfront?color=%2334D058&label=pypi%20package" alt="PyPI package">
</a>
<a href="https://discord.gg/rRyM7zkZTf" target="_blank">
    <img src="https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square" alt="Discord">
</a>
<a href="https://x.com/statespace_tech" target="_blank">
    <img src="https://img.shields.io/badge/Statespace-black?style=flat-square&logo=x&logoColor=white" alt="X">
</a>
</p>

---

**Source code: [https://github.com/statespace-tech/toolfront](https://github.com/statespace-tech/toolfront)**

---

ToolFront is a declarative framework for building modular AI applications in Markdown. Write tools and instructions in `.md` files, run the project, and get a live AI application.

## Simple Example

### Create it

  Start with one file: `README.md`


  ```markdown title="README.md"
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

=== ":simple-python: &nbsp; Python SDK"

    ```python
    from toolfront import Application

    app = Application(url="http://127.0.0.1:8000")

    result = app.ask("Is the service up?", model="openai:gpt-5")
    
    print(result)
    # Answer: yes
    ```

=== ":simple-modelcontextprotocol: &nbsp; MCP Server"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", "http://127.0.0.1:8000"],
        }
      }
    }
    ```

---

## Upgraded Example

Your full project can grow like this: 

```bash
project/
├── README.md #(1)!
├── src/
│   ├── api.md
│   ├── rag.md
│   ├── text2sql.md
│   └── toolkit.md
├── data/
└── tools/
```

1. All applications must have a `README.md`

### Add Navigation

  Update `README.md` with tools to explore the project.

  ```markdown title="README.md" hl_lines="4-5 11"
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

  Give your agent tools to search documents.

  ```markdown title="src/rag.md"
  ---
  tools:
    - [grep]
  ---

  # Search Docs
  - Use `grep` to search files in `/data/`
  ```

### Add Text-to-SQL

  Connect your databases for SQL workflows.


  ```markdown title="src/text2sql.md"
  ---
  tools:
    - [psql, -U, $USER, -d, $DATABASE, -c, {query}]
  ---

  # Database Access
  - Call the `psql` tool to query the PostgreSQL database
  ```

### Add Custom Tools

  Build custom tools in any programming language.

  ```markdown title="src/toolkit.md"
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

!!! toolfront "Deploy your Apps 🔥"

    Instantly deploy your AI applications:

    ```bash
    toolfront deploy ./path/to/project
    ```

    Gives you a shareable application URL:

    === ":material-web: Community Cloud (Free)"

        ```python
        # Up to 5 public apps, totally free
        app = Application("https://cloud.statespace.com/you/status-checker")
        ```

    === ":material-account-group: Statespace Cloud (Pro)"

        ```python
        # Up to 20 public or private apps with authentication
        app = Application("https://cloud.statespace.com/team/project", params={"API_KEY": "..."})
        ```

    === ":material-lock: Self-Hosted (Enterprise)"

        ```python
        # Unlimited on-prem apps with Docker or K8s  
        app = Application("https://custom.com/agent")
        ```
    
    [Get started for free](#){ .md-button .md-button--primary }
        
<p align="right"><strong>Made with ❤️ by <a href="https://statespace.com" target="_blank">Statespace</a></strong>.</p>
