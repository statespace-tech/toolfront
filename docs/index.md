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
    <em>Data environments for AI agents</em>
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

ToolFront helps you organize AI workflows into independent tasks with **environments**. 

=== ":material-home:{ .middle } &nbsp; Landing Page"

    Declare task instructions and tools in Markdown files.

    <div class="grid cards" markdown>

    ```bash hl_lines="2"
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

    </div>

=== ":material-database:{ .middle } &nbsp; Text-to-SQL"

    Create text-to-SQL tasks with ToolFront's built-in **[database CLI](./pages/database_cli.md)**

    <div class="grid cards" markdown>

    ```bash hl_lines="4"
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

    </div>


=== ":material-file-document:{ .middle } &nbsp; Document RAG"

    Retrieve information from data files like `.txt`, `.csv`, and `.json`.
      
    <div class="grid cards" markdown>

    ```bash hl_lines="5 7-9"
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

    </div>


=== ":material-api:{ .middle } &nbsp; API Integration"

      Fetch live data with calls to external APIs.

      <div class="grid cards" markdown>

      ```bash hl_lines="6"
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

      </div>

Agents browse environments to get work done, using tools and following instructions as needed.

=== ":simple-python:{ .middle } &nbsp; Python SDK"

    Run Python agents on environments with the **[SDK](./pages/python_sdk.md)**

    ```python
    from toolfront import Environment

    env = Environment(url="file:///path/environment")

    response = env.run("What's our average ticket size?", model="openai:gpt-5")
    ```

=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP Server"

    Connect your own agents to environments with the **[MCP Server](./pages/mcp_server.md)**

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", "file:///path/environment"],
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

=== ":fontawesome-brands-python:{ .middle } &nbsp; poetry"

    ```bash
    poetry add toolfront
    ```


!!! toolfront "Deploy with ToolFront Cloud 🔥"

    Instantly deploy your environments with **[ToolFront Cloud](pages/toolfront_cloud.md)**.

    ```bash
    toolfront deploy ./path/environment
    ```

    This gives you a secure environment URL your agents can access from anywhere.

    ```python
    Environment(url="https://cloud.toolfront.ai/user/environment", params={"API_KEY": ...})
    ```

    ToolFront Cloud is in beta. To request access, join our **[Discord](https://discord.gg/rRyM7zkZTf)** or email `esteban[at]kruskal[dot]ai`.