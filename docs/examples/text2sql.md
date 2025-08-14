# Text2SQL with Snowflake and GPT-4o

In this example, we'll convert natural language questions into SQL queries and get results from Snowflake data warehouse. GPT-4o's advanced reasoning capabilities make it excellent for complex SQL generation across multiple tables and joins.

## 1. Export your OpenAI API key.

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

## 2. Query your Snowflake data warehouse in English

```python linenums="1"
from toolfront import Database

# Connect to your Snowflake data warehouse
db = Database(
    "snowflake://user:pass@account/warehouse/database", 
    model="openai:gpt-4o"
)

# Get top performing products with natural language
top_products: list[str] = db.ask(
    "What are the top 5 best-selling products by revenue in the last quarter?"
)

print(f"Top {len(top_products)} products:")
for i, product in enumerate(top_products, 1):
    print(f"{i}. {product}")

>>> Top 5 products:
>>> 1. Wireless Headphones Pro
>>> 2. Gaming Laptop Elite
>>> 3. Smart Watch Series 3
>>> 4. Bluetooth Speaker Max
>>> 5. USB-C Hub Deluxe
```

!!! tip "SQL Generation"
    GPT-4o automatically handles complex JOINs, aggregations, and date filtering. No SQL knowledge required - just ask natural language questions about your data.