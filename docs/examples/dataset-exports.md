# Dataset Exports with PostgreSQL 

In this example, we'll export large datasets (100K+ rows) from PostgreSQL using structured Pydantic models for field validation and data consistency. Database exports bypass LLM token limits for massive data retrieval.

## 1. Export your OpenAI API key.

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

## 2. Define your data model and export structured datasets.

```python linenums="1"
from toolfront import Database
from pydantic import BaseModel, Field

class Customer(BaseModel):
    customer_id: int = Field(..., description="Unique customer identifier")
    name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer email address")
    total_orders: int = Field(..., ge=0, description="Number of orders placed")
    lifetime_value: float = Field(..., ge=0, description="Total customer spend")

# Connect to PostgreSQL database
db = Database("postgresql://user:pass@host/db", model="openai:gpt-4o")

# Export structured dataset with field validation
customers: db.Table[Customer] = db.ask(
    "Get all customer data with ID, name, email, order count, and total spent"
)

# Process the exported data
df = customers.to_dataframe()
high_value = df[df['lifetime_value'] > 5000]

print(f"Exported {len(customers):,} customers")
print(f"High-value customers: {len(high_value):,}")
print(f"Average LTV: ${df['lifetime_value'].mean():.2f}")

>>> Exported 125,847 customers
>>> High-value customers: 3,421
>>> Average LTV: $1,247.83
```

!!! tip "Dataset Exports"
    Use `db.Table[Model]` to export massive datasets with Pydantic validation. Data is streamed efficiently without LLM token costs, perfect for ETL workflows.