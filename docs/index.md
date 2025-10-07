---
title: "Data Environments for AI Agents"
description: "Build and deploy data environments your own agents can browse."
---

<style>
.md-content .md-typeset h1 { display: none; }
</style>


<p align="center">
  <a href="https://github.com/statespace-ai/toolfront">
    <img src="https://raw.githubusercontent.com/statespace-ai/toolfront/main/img/logo.png" alt="ToolFront" style="width:20%;">
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
├── page/
│   ├── cli.py
│   └── index.md
└── data/
    ├── sample.txt
    └── data.csv
```


To add actions to an environment, simply define commands in any markdown header. As agents browse files, they will discover these tools and learn how to use them with the `--help` flag.

```markdown title="index.md"
---
tools:
- [python3, cli.py]
- [curl, -X, GET, https://api.example.com/data]

---

# My environment page

Add [links](./page_1) to tell your agents what pages they should check out.

Agents can call any command defined in markdown headers.
- `python3 cli.py` executes a python script
- `curl -X GET https://api.example.com/data` calls an API
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

ToolFront's comes with six core tools[^1] your agents can use to interact with environments:

- :material-play:{ .middle } `run_command` - Execute commands defined in markdown headers
- :material-eye:{ .middle } `read` - Get the content of a specific page or file
- :material-regex:{ .middle } `glob` - List files matching a pattern
- :material-file-tree:{ .middle } `tree` - View directory structure
- :material-text-search:{ .middle } `grep` - Find relevant lines that match a regular expression 
- :material-magnify:{ .middle } `search` - Find relevant documents containing a list of terms

[^1]: `grep` and `search` require indexing environments.

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

    Instantly deploy your environments with **ToolFront Cloud**
    
    ```bash
    toolfront deploy ./path/to/environment --api-key "my-api-key"
    ```
    
    Would give you a secure environment URL your agents can browse.

    ```python
    from toolfront import Browser

    browser = Browser(params={"TOOLFRONT_API_KEY": "my-api-key"})

    answer = browser.ask(..., url="https://cloud.toolfront.ai/user/environment")
    ```

    Environments deployed to **ToolFront Cloud** are automatically indexed and get access to `grep` and `search` tools.

    ```
    I need to find information about ticket pricing APIs.
    Let me search the environment for "ticket pricing API"...

    Found 3 relevant pages:
      - ./api/pricing.md (highly relevant)
      - ./guides/analytics.md (relevant)
      - ./examples/queries.md (somewhat relevant)

    I'll start by reading ./api/pricing.md
    ```

    **ToolFront Cloud** is currently in open beta. To request access, join our [Discord](https://discord.gg/rRyM7zkZTf) or email `esteban[at]kruskal[dot]ai`.