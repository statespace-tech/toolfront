---
hide:
  - title
  - header
  - footer
  # - navigation
  # - toc
---
# FastAPI { #fastapi }

<style>
.md-content .md-typeset h1 { display: none; }
</style>

<p align="center">
  <a href="https://github.com/kruskal-labs/toolfront">
    <img src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/logo.png" alt="ToolFront" style="width:20%;">
  </a>
</p>
<p align="center">
    <em>Data retrieval environments for AI agents</em>
</p>
<p align="center">
<a href="https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml" target="_blank">
    <img src="https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml/badge.svg" alt="Test Suite">
</a>
<a href="https://pypi.org/project/toolfront/" target="_blank">
    <img src="https://img.shields.io/pypi/v/toolfront?color=%2334D058&label=pypi%20package" alt="PyPI package">
</a>
<a href="https://discord.gg/rRyM7zkZTf" target="_blank">
    <img src="https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square" alt="Discord">
</a>
<a href="https://x.com/toolfront" target="_blank">
    <img src="https://img.shields.io/badge/ToolFront-black?style=flat-square&logo=x&logoColor=white" alt="X">
</a>
</p>
---

**Documentation: [docs.toolfront.ai](http://docs.toolfront.ai/)**

**Source code: [https://github.com/kruskal-labs/toolfront](https://github.com/kruskal-labs/toolfront)**

---

**ToolFront** turns your markdowns and scripts into interactive sites for your AI agents. You can add arbitrary logic and context to these environments to help your agent retrieve the data you need.

```bash
toolsite/
├── index.md
├── page_1/
│   ├── cli.py
│   └── index.md
└── page_2/
    ├── cli.rs
    └── index.md
```

---

**Markdown** pages define instructions and commands for your AI agents. `tool` commands can be called by agents, 
while `content` commands dynamically add context to your pages.

=== ":fontawesome-brands-markdown:{ .middle } &nbsp; Instructions"

    ```markdown hl_lines="9-16"
    ---
    tool:
    - [python3, cli.py]
    - [curl, https://api.example.com/data]
    content
    - [echo, "$USER"]
    ---

    # My toolsite

    You are a business analyst. Your goal is to answer the user's question.

    Run `cli.py` to retrieve the latest orders.

    Go to ./page_1 to learn about our products, or ./page_2 to learn about customers.
    ```

=== ":fontawesome-solid-terminal:{ .middle } &nbsp; Commands"

    ```markdown hl_lines="1-7"
    ---
    tool:
    - [python3, cli.py]
    - [curl, https://api.example.com/data]
    content
    - [echo, "user: $USER"]
    ---

    # My toolsite

    You are a business analyst. Your goal is to answer the user's question.

    Run `cli.py` to retrieve the latest orders.

    Go to ./page_1 to learn about our products, or ./page_2 to learn about customers.
    ```



!!! question "Tool instructions"
    ToolFront automatically runs the `--help` flag on each tool command and passes the instructions to your agent.

---

**Browsers** help AI agents navigate environment pages and use tools. You can use ToolFront's python SDK for rapid development, or the MCP
 if you want more control of your agent.


=== ":simple-python:{ .middle } &nbsp; SDK"
    ```python
    from toolfront import Browser
    from pydantic import BaseModel

    browser = Browser(model="openai:gpt-5")
    url = "file:///path/to/toolsite"

    answer = browser.ask("What's our average ticket price?", url=url)

    answer = browser.ask("Average ticket price?", url=url, output_type=float) # (1)!

    class Customer(BaseModel):  # (2)!
        name: str = Field(..., description="Customer name")
        seats: int = Field(..., description="Number of seats")

    answer = browser.ask("Who's our best customer?", url=url, return_type=Customer)
    ```

    1. Setting the `output_type` parameter makes the agent return data in the type you specify (e.g., scalars, collections, dataclasses, Pydantic models, unions, or functions).
    2. Adding Pydantic field descriptions improves performance.


=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP"
    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront", 
            "browser", 
            "serve", 
            "file:///path/to/toolsite",
            "--transport",
            "stdio"
          ]
        }
      }
    }
    ```


!!! question "Installation"
    Install the `toolfront` browser with `pip` or your favorite PyPI package manager: `pip install toolfront`

---

**Models** can use ToolFront's browser to navigate pages and call tools. The browser works with all major cloud model providers, as well as local models.

=== ":fontawesome-solid-cloud:{ .middle } &nbsp; Cloud"

    ```python
    from toolfront import Browser

    # OpenAI
    browser = Browser(model="openai:gpt-4o")

    # Anthropic
    browser = Browser(model="anthropic:claude-3-5-sonnet-20241022")
  
    # Google
    browser = Browser(model="google:gemini-1.5-pro")
    ```

=== ":fontawesome-solid-desktop:{ .middle } &nbsp; Local"

    ```python
    from toolfront import Database
    from pydantic_ai.models.openai import OpenAIChatModel

    ollama_model = OpenAIChatModel(
        'llama3.2',
        base_url='http://localhost:11434/v1',
        api_key='ignored',
    )

    db = Browser("postgres://user:pass@localhost:5432/mydb", model=ollama_model)
    ```




---


**Hosting** markdown pages can be done on any filesystem supported by [fsspec](https://filesystem-spec.readthedocs.io/). Use the browser's `params` to 
authenticate with your filesystem.

=== ":fontawesome-solid-folder:{ .middle } &nbsp; Filesystem"

    ```python

    browser = Browser(params=None)

    result = browser.ask(..., url="file:///path/to/toolsite")
    ```

=== ":fontawesome-solid-bucket:{ .middle } &nbsp; S3"

    ```python
    browser = Browser(params={"key": "ACCESS_KEY", "secret": "SECRET_KEY"})

    result = browser.ask(..., url="s3://my-bucket/toolsite")
    ```

=== ":simple-github:{ .middle } &nbsp; GitHub"

    ```python
    browser = Browser(params={"username": "user", "token": "ghp_token"})

    result = browser.ask(..., url="github://company/repo/toolsite")
    ```



!!! toolfront "Deploy with ToolFront's API  🔥"

    Markdown pages can be hosted anywhere, but scripts need separate hosting. 
    ToolFront's API hosts and deploys entire environments with both markdown pages and command scripts:


    ```bash
    toolfront deploy ./path/to/toolsite.
    ```

    Would give you a securely hosted environment you AI agents can browse:

    ```python
    from toolfront import Browser

    browser = Browser(params={"api_key": "YOUR-TOOLFRONT-API-KEY"})

    result = browser.ask(..., url="https://api.toolfront.ai/user/mysite")
    ```

    [**Learn more about the ToolFront API**](https://toolfront.ai/)



