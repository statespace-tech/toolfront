# Retrieval

ToolFront makes it easy to retrieve data in natural language.

---

## Simple Responses

Directly calling your data source's `ask()` method will return a string.

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-database:{ .middle } &nbsp; Databases"

    ```python linenums="1"
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    result = db.ask("What's our total revenue this quarter?")
    print(result)
    # Returns: "Total revenue for Q4 2024 is $2.4M"
    ```

=== ":fontawesome-solid-code:{ .middle } &nbsp; APIs"

    ```python linenums="1"
    from toolfront import API

    api = API("https://api.example.com/openapi.json")

    result = api.ask("Get the latest status for service XYZ")
    print(result)
    # Returns: "Service XYZ is running with 99.9% uptime"
    ```

=== ":fontawesome-solid-file:{ .middle } &nbsp; Documents"

    ```python linenums="1"
    from toolfront import Document

    doc = Document("/path/to/annual_report.pdf")
    
    result = doc.ask("What were the key achievements this year?")
    print(result)
    # Returns: "Key achievements include 30% revenue growth..."
    ```

</div>

---

## Typed Responses

Add a type hint to `ask()` to specify the exact Python type you want returned:

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-cube:{ .middle } &nbsp; Primitives"

    ```python linenums="1"
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    total_orders: int = db.ask("How many orders do we have?")
    # Returns: 1250

    avg_price: float = db.ask("What's our average ticket price?")
    # Returns: 29.99

    best_product: str = db.ask("What's our best-selling product?")
    # Returns: "Wireless Headphones Pro"

    has_inventory: bool = db.ask("Do we have any monitors in stock?")
    # Returns True
    ```

=== ":fontawesome-solid-layer-group:{ .middle } &nbsp; Collections"

    ```python linenums="1"
    from toolfront import API

    db = API("https://api.com/openapi.json")

    # Lists
    product_names: list[str] = db.ask("What products do we sell?")
    # Returns: ["Laptop Pro", "Wireless Mouse", "USB Cable"]

    # Dictionaries  
    sales_by_region: dict[str, int] = db.ask("Sales by region")
    # Returns: {"North": 45000, "South": 38000, "East": 52000}

    # Sets (unique values)
    active_regions: set[str] = db.ask("Which regions have sales?")
    # Returns: {"North America", "Europe", "Asia Pacific"}
    ```

=== ":fontawesome-solid-chain:{ .middle } &nbsp; Unions"

    ```python linenums="1"
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    price: int | float = db.ask("Price of product XYZ?")
    # Returns: 29.99, 30

    result: str | list[str] = db.ask("Best-sellers this month?")
    # Returns: ["Product A", "Product B"] or "No data found"

    error: str | None = db.ask("What was the error message?")
    # Returns: "Connection timeout" or None

    status: bool | str = db.ask("Is the system healthy?")
    # Returns: True or "Database connection failed"
    ```

=== ":fontawesome-solid-sitemap:{ .middle } &nbsp; Pydantic Objects"

    ```python linenums="1"
    from toolfront import Document
    from pydantic import BaseModel, Field
    from typing import List

    db = Document("path/to/document.pdf")

    class Product(BaseModel):
        name: str = Field(..., description="Product name") # (1)
        price: float | int = Field(..., description="Product price in USD")
        in_stock: bool = Field(..., description="Product is in stock")


    # Outputs a structured Pydantic object
    product: Product = db.ask("What's our best-selling product") 
    # Returns: Product(name="Blue Headphones", price=300, in_stock=True) # (2)
    ```
    
    1. Adding a Pydantic field descriptions improves retrieval accuracy.
    2. You can also retrieve collections of Pydantic objects, e.g. `products: list[Product] = db.ask(...)`

</div>

!!! tip "Alternative: Output Type Parameter"
    Instead of type annotations, you can specify the output type using the `output_type` parameter:
    
    ```python
    total_orders = db.ask("How many orders do we have?", output_type=int)
    ```

---

## Dataset Exports

Retrieve massive datasets without incurring additional LLM token costs.


<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-table:{ .middle } &nbsp; As-Is"

    ```python linenums="1" hl_lines="6"
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    # Export 100,000+ rows
    sales_data: db.Table = db.ask("Get all sales from 2024")

    # Process locally
    df = sales_data.to_dataframe()
    print(f"Retrieved {len(df):,} rows")

    # Export formats
    sales_data.to_csv("sales_2024.csv")
    sales_data.to_excel("report.xlsx")
    print(sales_data.columns)
    ```

=== ":fontawesome-solid-list:{ .middle } &nbsp; Specific Fields"

    ```python linenums="1" hl_lines="6-9 12"
    from toolfront import Database
    from pydantic import BaseModel

    db = Database("postgresql://user:pass@host/db")

    class Sale(BaseModel):
        customer_name: str
        amount: float
        date: str

    # Specify columns fields to retrieve with Pydantic
    sales_data: db.Table[Sale] = db.ask("Get Q4 sales") # (1)

    for sale in sales_data:
        print(f"{sale.customer_name}: ${sale.amount}")
    ```
    
    1. `sales_data` can also be converted to a DataFrame with `sales_data.to_dataframe()`

</div>

!!! warning "Database-Only"
    Dataset exports are only supported for databases.

---

## Adding Context

You can provide additional business context to improve the accuracy of responses using the `context` parameter:

```python linenums="1"
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Add business context for better understanding
context = """
Our company operates in the fashion industry.
Revenue is measured quarterly, and our fiscal year starts in April.
Product categories include: clothing, accessories, footwear.
"""

result = db.ask(
    "What's our total revenue this quarter?",
    context=context
)
print(result)
# Returns more contextually accurate result
```

---

## Error Handling

Handle failures with error strings, or models, or custom output validation.

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-exclamation-triangle:{ .middle } &nbsp; Error Strings"

    ```python linenums="1"
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    # Success returns data, failure returns error string
    result: list[dict] | str = db.ask("Complex query that might fail")
    # Returns: [{"id": 1, "name": "John"}] or "Error: table not found"

    # Handle both success and error cases
    status: bool | str = db.ask("Is the system healthy?")
    # Returns: True or "Database connection failed"

    if isinstance(result, str):
        print(f"Error: {result}")
    else:
        print(f"Found {len(result)} records")
    ```

=== ":fontawesome-solid-cog:{ .middle } &nbsp; Error Models"

    ```python linenums="1" hl_lines="6-9"
    from toolfront import Database
    from pydantic import BaseModel

    db = Database("postgresql://user:pass@host/db")

    class DatabaseError(BaseModel):
        error_type: str
        message: str
        suggestion: str

    # Handle both success and error cases
    result: list[dict] | DatabaseError = db.ask("Complex query")
    # Returns: list[dict] or DatabaseError

    if isinstance(result, DatabaseError):
        print(f"Error: {result.message} | Suggestion: {result.suggestion}")
    ```

=== ":fontawesome-solid-shield-alt:{ .middle } &nbsp; Output Validation"

    ```python linenums="1" hl_lines="6-13"
    from toolfront import Database
    from pydantic import BaseModel, Field, validator

    db = Database("postgresql://user:pass@host/db")

    class Customer(BaseModel):
        name: str = Field(..., min_length=1)
        email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
        age: int = Field(..., ge=0, le=120)
        
        @validator('email')
        def validate_email(cls, v):
            return v.lower()

    # Pydantic automatically validates responses
    customers: list[Customer] = db.ask("Get all customers")
    ```

</div>