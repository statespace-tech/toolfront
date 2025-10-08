---
title: "Data Environments for AI Agents"
description: "Build and deploy data environments your own agents can browse."
---

<style>
.md-content .md-typeset h1 { display: none; }
</style>


<p align="center">
  <a href="https://github.com/statespace-ai/toolfront">
    <img src="assets/img/logo.svg" alt="ToolFront" style="width:20%;">
  </a>
</p>
<p align="center">
    <strong><em>Data environments for AI agents</em></strong>
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
    # Sales Analytics Environment

    You are a business analyst at an e-commerce company.
    Answer questions about company sales data and customer activity.
    Navigate to different pages to access various data sources.

    - Go to [database](./pages/database.md) to query sales transactions
    - Go to [Documents](./pages/document.md) to read customer receipts
    - Go to [API](./pages/api.md) to fetch real-time pricing data
    ```

=== "Text-to-SQL Page"
    ```markdown title="database.md"
    ---
    tools:
      - [toolfront, database, list-tables]
      - [toolfront, database, inspect-table]
      - [toolfront, database, query]

    ---

    # Database Page

    Use ToolFront's built-in commands to explore tables and run SQL queries:
    - `toolfront database list-tables` shows available tables
    - `toolfront database inspect-table` displays a table's schema
    - `toolfront database query` runs SQL queries on the data
    ```

=== "Document RAG Page"
    ```markdown title="document.md"
    # Documents Page

    Read customer receipts stored as plain text files in `../data/`.
    Filenames use timestamped IDs (e.g., `receipt_20240115_001.txt`).

    - `receipt_20240115_001.txt` contains a January 15th transaction
    - `receipt_20240118_002.txt` contains a January 18th transaction
    - Files include customer info, line items, and payment details
    ```

=== "API Integration Page"
    ```markdown title="api.md"
    ---
    tools:
      - [curl, -X, GET, "https://api.products.com/v1/pricing"]
      - [curl, -X, GET, "https://api.products.com/v1/inventory"]
    
    ---

    # API Page

    Fetch real-time pricing and inventory from the product management API.
    Use the provided curl commands to retrieve JSON data.

    - `curl -X GET https://api.products.com/v1/pricing` gets current prices
    - `curl -X GET https://api.products.com/v1/inventory` checks stock levels
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