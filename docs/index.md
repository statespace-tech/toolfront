---
title: "Quickstart"
---

<p align="center">
  <a href="https://github.com/statespace-tech/toolfront">
    <img src="assets/images/logo.png" alt="ToolFront" style="width:20%;">
  </a>
</p>
<div align="center">
    <h1 style="font-weight: 800;"><b>ToolFront</b></h1>
</div>
<p align="center">
    <em>Build AI Applications in Markdown</em>
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

<b> ToolFront is a declarative framework for building AI applications in Markdown.</b>

=== ":material-home: Entry Point"

    Start by creating a README with general instructions and tools for your agent.

    <div class="grid cards" markdown>

    ```bash hl_lines="3"
    project/
    ├── data/
    ├── README.md
    ├── spec.json
    ├── src/
    │   ├── api.md
    │   ├── rag.md
    │   ├── text2sql.md
    │   └── toolkit.md
    └── tools/

    4 directories, 30 files
    ```

    ```markdown title="README.md"
    ---
    tools:
      - [ls]
      - [cat]
    
    ---

    # Agent Instructions
    - Use `ls` and `cat` to browse the tool site
    - Check out `./src` for specialized workflows
    ```

    </div>

=== ":material-web: API Integration"

    Connect agents to external APIs and web services using HTTP tools like `curl`.

    <div class="grid cards" markdown>

    ```bash hl_lines="6"
    project/
    ├── data/
    ├── README.md
    ├── spec.json
    ├── src/
    │   ├── api.md
    │   ├── rag.md
    │   ├── text2sql.md
    │   └── toolkit.md
    └── tools/

    4 directories, 30 files
    ```


    ```markdown title="api.md"
    ---
    tools:
      - [curl, -X, GET, "https://api.com/{endpoint}"]

    ---

    # Web API
    - Call external APIs to fetch real-time data.
    - Pass `{endpoint}` to make GET requests
    - Check `/data/spec.json` for available endpoints
    ```

    </div>

=== ":material-file-document: Document RAG"

    Teach your agent how to search and interpret documents with tools like `grep`.

    <div class="grid cards" markdown>

    ```bash hl_lines="7"
    project/
    ├── data/
    ├── README.md
    ├── spec.json
    ├── src/
    │   ├── api.md
    │   ├── rag.md
    │   ├── text2sql.md
    │   └── toolkit.md
    └── tools/

    4 directories, 30 files
    ```


    ```markdown title="rag.md"

    ---
    tools
      - [grep]
    
    ---

    # Document RAG
    - Use `grep` to search through `/data/catalog/`
    - Cross-reference information across documents
    - Look for product IDs, SKUs, or feature details
    ```

    </div>


=== ":material-database: Text-to-SQL"

    Connect agents to databases using CLI tools like `psql` for text-to-SQL workflows.

    <div class="grid cards" markdown>

    ```bash hl_lines="8"
    project/
    ├── data/
    ├── README.md
    ├── spec.json
    ├── src/
    │   ├── api.md
    │   ├── rag.md
    │   ├── text2sql.md
    │   └── toolkit.md
    └── tools/

    4 directories, 30 files
    ```

    ```markdown title="text2sql.md"
    ---
    tools:
      - [psql, -U, $USER, -d, $DATABASE, -c, {query}]
    
    ---

    # Text-to-SQL 
    - Query the PostgreSQL DB for product details
    - Pass a `{query}` to the `psql` tool
    - Available tables: `products` and `categories`
    ```

    </div>


=== ":material-tools: Custom Tools"

    Build custom tools using scripts in any programming language.

    <div class="grid cards" markdown>

    ```bash hl_lines="9"
    project/
    ├── data/
    ├── README.md
    ├── spec.json
    ├── src/
    │   ├── api.md
    │   ├── rag.md
    │   ├── text2sql.md
    │   └── toolkit.md
    └── tools/

    4 directories, 30 files
    ```


    ```markdown title="toolkit.md"
    ---
    tools:
      - [python, tools/status.py, {id}]
      - [cargo, script, tools/check_delays.rs]

    ---

    # Toolkit
    - Run `status.py` with `{id}` to check statuses
    - Use `check_delays.rs` to scan for delayed orders
    ```

    </div>

Once you've built your application, run it with `toolfront run ./path/to/project`:

```bash
$ toolfront run ./path/to/project --port 8000
INFO:     Started server process [72194]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Agents can interact with running applications in one of two ways:

=== ":simple-python:{ .middle } &nbsp; Python SDK"

    ToolFront's Python SDK provides a pre-built application interface in Python

    ```python
    from toolfront import Application

    app = Application(url="http://127.0.0.1:8000")

    result = app.ask("What's the status of order 66?", model="openai:gpt-5")
    ```

=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP Server"

    ToolFront's MCP Server lets you connect your own agents to running applications.

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

To get started, install `toolfront` with your favorite PyPI package manager.

=== ":fontawesome-brands-python:{ .middle } &nbsp; pip"

    ```bash
    pip install toolfront
    ```

=== ":simple-uv:{ .middle } &nbsp; uv"

    ```bash
    uv add toolfront
    ```

=== ":simple-poetry:{ .middle } &nbsp; poetry"

    ```bash
    poetry add toolfront
    ```


!!! toolfront "Deploy to ToolFront Cloud 🔥"

    Instantly deploy your AI applications with **[ToolFront Cloud](pages/toolfront_cloud.md)**.

    ```bash
    toolfront deploy ./path/to/project
    ```

    This gives you a secure application URL you can access from anywhere.

    ```python
    app = Application(url="https://cloud.toolfront.ai/user/project", params={"API_KEY": ...})
    ```

    ToolFront Cloud is in beta. To request access, join our **[Discord](https://discord.gg/rRyM7zkZTf)** or email `esteban[at]statespace[dot]com`.