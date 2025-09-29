# Text2SQL

Build a simple Text2SQL environment for querying your database with natural language.

## 1. Installation

Install ToolFront with the necessary database extras for your specific database type.

```bash
pip install "toolfront[postgres]"
```

## 2. Export API Key

Configure your LLM API key so ToolFront can access your chosen model.

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## 3. Create Environment

Create a simple directory structure with a single markdown file that defines your database environment.

```bash
mysite/
└── index.md
```

## 4. Add Markdown Page

Create `./mysite/index.md` with ToolFront's built-in database commands. These tools allow your AI agent to explore and query your database.

```markdown
---
- [toolfront, database, list-tables]
- [toolfront, database, inspect-table]
- [toolfront, database, query]
---

# Database Analysis

You are a business analyst. Answer questions using only data from the database.
Use the database tools to explore tables and run queries.

Use the `orders` table to find sales data and customer purchase information.
Use the `products` table to find product details, pricing, and inventory levels.
Use the `customers` table to find customer demographics and contact information.
```

## 5. Query Your Data

Initialize a Browser instance and ask natural language questions about your database. The AI will automatically use the database tools to find answers.

```python
from toolfront import Browser

browser = Browser(
    model="openai:gpt-4o",
    env={"POSTGRES_URL": "postgres://user:pass@localhost:5432/mydb"}
)

url = "file://path/to/mysite"

response = browser.ask("What's our best-selling product?", url=url)

response: list[int] = browser.ask("What are the IDs of all products with sales over 1000 units?", url=url")
```

!!! tip "Environment Variables"
    The `env` variables are passed to tools but never exposed to the LLM, keeping your credentials secure. The LLM can still forward variable names to tools when needed.

