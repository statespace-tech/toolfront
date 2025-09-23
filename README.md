<p align="center">
  <a href="https://github.com/kruskal-labs/toolfront">
    <img src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/logo.png" width="150" alt="ToolFront Logo">
  </a>
</p>

<div align="center">

*Data retrieval environments for AI agents*

[![Test Suite](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml)
[![PyPI package](https://img.shields.io/pypi/v/toolfront?color=%2334D058&label=pypi%20package)](https://pypi.org/project/toolfront/)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square)](https://discord.gg/rRyM7zkZTf)
[![X](https://img.shields.io/badge/ToolFront-black?style=flat-square&logo=x&logoColor=white)](https://x.com/toolfront)

</div>


---

**Documentation: [docs.toolfront.ai](http://docs.toolfront.ai/)**

---

## Installation

Install with `pip` or your favorite PyPI package manager.

```bash
pip install toolfront
```

## Quickstart

ToolFront turns markdowns and scripts into navigable sitemaps for your AI agents.

```bash
mysite/
├── index.md
├── hello.py
├── database/
│   └── index.md
├── documents/
│   ├── index.duckdb
│   └── index.md
└── analytics/
    ├── index.md
    └── cli.py
```
Each `.md` file can have *markdown* instructions and *command* tools.

```markdown
---
[python3, tool.py]
---

# My toolsite

You are a business analyst. Your goal is to answer the user's quesiton.

Run `tool.py` to be greeted by a welcome message!

Go to ./database to find out more about the user's data.
```

AI can browse these sitemaps by following links and executing commands to retrieve data and find answers.

```python
from toolfront.browser import Browser

browser = Browser(model="openai:gpt-4o")

response = browser.ask("What's our best-selling product?", url="./mysite")
```
## Example 1: Landing Page

Create `./mysite/index.md`:

```markdown
# My toolsite

You are a business analyst. Your goal is to answer the user's quesiton.

Always answer the user's question using ONLY data explicitly retrieved through the provided tools.

## General Instructions
* NEVER make assumptions, hallucinate data, or supplement answers with general knowledge
* Present findings in markdown or the desired output type.
* Thoroughly try multiple approaches before concluding data cannot be found
* Handle missing or incomplete data by filtering values before giving up
* If no relevant data can be found after exhaustive retrieval attempts, clearly explain why

## Available pages:
- Go to ./database to query and analyze tables
- Go to ./documents to search through documents
- Go to ./analytics for custom data analysis
```

## Example 2: Text2SQL Page

Create `./site/database/index.md` with ToolFront's built-in `database` commands:

```markdown
---
- [toolfront, database, inspect-table]
- [toolfront, database, list-tables]
- [toolfront, database, query]
---

# Instructions

This page allows you to learn about the database: `postgres://user:pass@localhost:5432/mydb`

Use the inspect-table, list-tables, and query tools to navigate the database.
```

## Example 3: Document RAG page

1. Index a collection of `.txt`. documents by running `toolfront document index /path/to/documents`

2. Place the `duckdb.index` file under `./site/database`

3. Create `./site/database/index.md` with ToolFront's built-in `document` commands

```markdown
---
- [toolfront, document, search, './duckdb.index']
- [toolfront, document, read]
---

# Document Search

This page allows you to learn about your documents.

Use the search and read tools to find and read relevant documents.
```

## Example 4: Custom Page

Create a CLI program `./mysite/analytics/cli.py`:

```python
import click

@click.command()
@click.option('--metric', required=True, help='Metric to analyze: sales or revenue')
def analyze(metric):
    """Simple analytics tool"""

    if metric == 'sales':
        click.echo("Sales this month: 4,500 units")
        click.echo("Growth: +15%")
    elif metric == 'revenue':
        click.echo("Revenue this month: $125,000")
        click.echo("Growth: +12%")
    else:
        click.echo("Available metrics: sales, revenue")

if __name__ == '__main__':
    analyze()
```

Then, create `./mysite/analytics/index.md`

```markdown
---
- [python3, cli.py, --metric]
---

# Custom Analytics

View business metrics using a custom Python CLI tool.

Run cli.py with --metric sales or --metric revenue to see data.
```



## Browser MCP Server

You can directly use ToolFront Browser as an MCP:

```json
{
  "mcpServers": {
    "toolfront-browser": {
      "command": "uv",
      "args": [
        "run", 
        "toolfront", 
        "browser", 
        "serve",
        "./mysite",
        "--transport", 
        "stdio"
      ]
    }
  }
}
```
do
> **Note**: ToolFront supports OpenAI, Anthropic, Google, xAI, and 14+ AI model providers. See the [documentation](http://docs.toolfront.ai/) for the complete list.

## Community & Contributing

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **X**: Follow us [@toolfront](https://x.com/toolfront) for updates and news
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/kruskal-labs/toolfront/issues)

## License

This project is licensed under the terms of the MIT license.