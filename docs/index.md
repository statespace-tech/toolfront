---
title: "Quickstart"
---

<p align="center">
  <a href="https://github.com/statespace-ai/toolfront">
    <img src="assets/images/logo.svg" alt="ToolFront" style="width:20%;">
  </a>
</p>
<div align="center">
    <h1 style="font-weight: 800;"><b>ToolFront</b></h1>
</div>
<p align="center">
    <em>Data environments for AI agents</em>
</p>
<p align="center">
<a href="https://github.com/statespace-ai/toolfront/actions/workflows/test.yml" target="_blank">
    <img src="https://github.com/statespace-ai/toolfront/actions/workflows/test.yml/badge.svg" alt="Test Suite">
</a>
<a href="https://pypi.org/project/toolfront/" target="_blank">
    <img src="https://img.shields.io/pypi/v/toolfront?color=%2334D058&label=pypi%20package" alt="PyPI package">
</a>
<a href="https://discord.gg/rRyM7zkZTf" target="_blank">
    <img src="https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square" alt="Discord">
</a>
<a href="https://x.com/statespace_ai" target="_blank">
    <img src="https://img.shields.io/badge/Statespace-black?style=flat-square&logo=x&logoColor=white" alt="X">
</a>
</p>

---

**Source code: [https://github.com/statespace-ai/toolfront](https://github.com/statespace-ai/toolfront)**

---

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

=== "Landing Page"
    ```markdown title="index.md"
    ---
    tools:
      - [date, +%Y-%m-%d]

    ---

    # Landing Page

    Your landing page sets global instructions and tools for agents.
    Add links to specialized pages (e.g., `./pages`) for different workflows.
    Define tools like `date` that work everywhere.
    ```

=== "Text-to-SQL"
    ```markdown title="database.md"
    ---
    tools:
      - [toolfront, database]

    ---

    # Database Page

    Use ToolFront's `database` CLI for text-to-SQL workflows.
    Agents can call subcommands like `list-tables`, `inspect-table`, and `query`,
    passing arguments as needed.
    ```

=== "Document RAG"
    ```markdown title="document.md"
    ---
    tools:
      - [python, extract_totals.py]

    ---

    # Documents Page

    Agents use built-in tools like `read`, `glob`, and `grep` to search files.
    Point to document directories like `../data/` where files are stored.
    Add custom commands (e.g., `extract_totals.py`) for structured extraction.
    ```

=== "API Integration"
    ```markdown title="api.md"
    ---
    tools:
      - [curl, -X, GET, "https://api.products.com/v1/pricing"]
    
    ---

    # API Page

    Define HTTP endpoints as executable tools using `curl` commands.
    Add headers like `-H "Authorization: Bearer $TOKEN"` for authenticated APIs.
    Agents can fetch live data by calling these commands with parameters.
    ```

You can launch browsing sessions with ToolFront's Python SDK, or build your own browsing agent with the MCP. Browsing is always powered by your own models.

=== ":simple-python:{ .middle } &nbsp; SDK"
    ```python
    from toolfront import Browser

    browser = Browser(model="openai:gpt-5")

    url = "file:///path/to/environment"

    answer = browser.ask("What's our average ticket price?", url=url)
    print(answer)
    ```


=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP"
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

ToolFront comes with six core tools your agents can use to interact with environments:

- :material-play:{ .middle } `run_command` - Execute commands defined in markdown headers
- :material-eye:{ .middle } `read` - Read the content of a specific file
- :material-file-tree:{ .middle } `tree` - View directory structure
- :material-folder-search:{ .middle } `glob` - List files matching a glob pattern
- :material-regex:{ .middle } `grep` - Search files using regex patterns
- :material-magnify:{ .middle } `search` - Find relevant documents using BM25 full-text search[^1]

[^1]: `search` requires indexing environment files.

To get started, install `toolfront` using your favorite PyPI package manager.

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