<p align="center">
  <a href="https://github.com/kruskal-labs/toolfront">
    <img src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/logo.png" width="150" alt="ToolFront Logo">
  </a>
</p>

<div align="center">

*Simple data retrieval for AI with unmatched control, precision, and speed.*

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

## Example 1: Text2SQL with ChatGPT

```python
from toolfront import Database

db = Database("postgres://user:pass@localhost:5432/mydb", model="openai:gpt-4o")

context = "We're an e-commerce company. Sales data is in the `cust_orders` table."

# Returns a string
answer = db.ask("What's our best-selling product?", context=context)
# >>> "Wireless Headphones Pro"
```

> **Note**: For databases, install with PyPI extras, e.g.: `pip install "toolfront[postgres]"`. See the [documentation](http://docs.toolfront.ai/) for the complete list of 10+ databases.

## Example 2: API retrieval with Claude

```python
from toolfront import API

api = API("http://localhost:8000/openapi.json", model="anthropic:claude-3-5-sonnet")

# Returns a list of integers
answer: list[int] = api.ask("Get the last 5 order IDs for user_id=42")
# >>> [1001, 998, 987, 976, 965]
```

> **Note**: ToolFront supports any API with an OpenAPI (formerly Swagger) specification. Most common APIs like Slack, Discord, and GitHub have OpenAPI specs. See the [documentation](http://docs.toolfront.ai/) for more details.


## Example 3: Document information extraction with Gemini

```python
from toolfront import Document
from pydantic import BaseModel, Field

class CompanyReport(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    revenue: int | float = Field(..., description="Annual revenue in USD")
    is_profitable: bool = Field(..., description="Whether the company is profitable")

doc = Document("/path/annual_report.pdf", model="google:gemini-pro")

# Returns a structured Pydantic object
answer: CompanyReport = doc.ask("Extract the key company information from this report")
# >>> CompanyReport(company_name="TechCorp Inc.", revenue=2500000, is_profitable=True)
```

> **Note**: ToolFront supports OpenAI, Anthropic, Google, xAI, and 14+ AI model providers. See the [documentation](http://docs.toolfront.ai/) for the complete list.


## Example 4: Snowflake MCP Server

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": [
        "toolfront[snowflake]", 
        "snowflake://user:pass@account/warehouse/database"
      ]
    }
  }
}
```

## Community & Contributing

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **X**: Follow us [@toolfront](https://x.com/toolfront) for updates and news
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/kruskal-labs/toolfront/issues)

## License

This project is licensed under the terms of the MIT license.