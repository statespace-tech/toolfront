# Browser


You agents can browse environments using ToolFront's Python SDK or MCP.


<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-code:{ .middle } &nbsp; SDK"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser("file:///path/to/mysite")

    result = browser.ask("What's our total revenue this quarter?")

    print(result)
    # Returns: "Total revenue for Q4 2024 is $2.4M"
    ```

=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP"

    ```json linenums="1"
    {
    "mcpServers": {
        "toolfront": {
            "command": "uvx",
            "args": ["toolfront", "browser", "serve", "file:///path/to/mysite"]
            }
        }
    }
    ```

</div>

!!! tip "Filesystem Support"
    ToolFront supports serving environments from virtually any filesystem (s3://, gcs://, azure://, etc.) through [fsspec](https://filesystem-spec.readthedocs.io/). Use `--params` to pass authentication credentials as needed.

---
## Python SDK

### Typed Responses

Add a type hint to `ask()` to specify the exact Python type you want returned:

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-cube:{ .middle } &nbsp; Primitives"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser("file://path/to/mysite")

    total_orders: int = browser.ask("How many orders do we have?")
    # Returns: 125

    avg_price: float = browser.ask("What's our average ticket price?")
    # Returns: 29.99

    best_product: str = browser.ask("What's our best-selling product?")
    # Returns: "Laptop Pro"

    has_inventory: bool = browser.ask("Do we have pending refunds?")
    # Returns: True
    ```

=== ":fontawesome-solid-layer-group:{ .middle } &nbsp; Collections"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser("https://api.company.com/docs")

    # Lists
    monthly_sales: list[int] = browser.ask("Monthly sales this year?")
    # Returns: [15000, 18000, 22000]

    # Dictionaries
    sales_by_region: dict[str, int] = browser.ask("Sales by region?")
    # Returns: {"North": 45000, "South": 38000}

    # Sets (unique values)
    unique_brands: set[str] = browser.ask("What brands do we carry?")
    # Returns: {"Apple", "Dell", "HP"}
    ```

=== ":fontawesome-solid-chain:{ .middle } &nbsp; Unions"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser("s3://analytics-bucket/reports")

    price: int | float = browser.ask("Price of product XYZ?")
    # Returns: 30 or 29.99

    result: list[str] | str = browser.ask("Best-sellers this month?")
    # Returns: ["Product A", "Product B"] or "Product C"

    error: str | None = browser.ask("What was the error message?")
    # Returns: "Connection timeout" or None

    status: bool | str = browser.ask("Is the system healthy?")
    # Returns: True or "Connection failed"
    ```

=== ":fontawesome-solid-sitemap:{ .middle } &nbsp; Pydantic Objects"

    ```python linenums="1"
    from toolfront import Browser
    from pydantic import BaseModel, Field

    browser = Browser("git://github.com/company/invoices")

    class Customer(BaseModel):
        name: str = Field(..., description="Customer name") # (1)
        seats: int = Field(..., description="Number of seats")
        is_active: bool = Field(..., description="Customer is active")


    # Outputs a structured Pydantic object
    customer: Customer = browser.ask("Who's our latest customer?")
    # Returns: Customer(name='Acme', seats=5, is_active=True) # (2)
    ```

    1. Adding Pydantic field descriptions improves retrieval accuracy.
    2. You can also retrieve collections of Pydantic objects, e.g. `customers: list[Customer] = browser.ask(...)`

</div>

!!! tip "Alternative: Output Type Parameter"
    Instead of type annotations, you can specify the output type using the `output_type` parameter:

    ```python
    total_orders = browser.ask("How many orders do we have?", output_type=int)
    ```

---

### Error Handling

Handle failures with error strings, or models, or custom output validation.

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-exclamation-triangle:{ .middle } &nbsp; Error Strings"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser("file://path/to/mysite")

    # Success returns data, failure returns error string
    result: list[dict] | str = browser.ask("Complex operation that might fail")
    # Returns: [{"id": 1, "name": "John"}] or "Error: file not found"

    # Handle both success and error cases
    status: bool | str = browser.ask("Is the system healthy?")
    # Returns: True or "Environment not accessible"

    if isinstance(result, str):
        print(f"Error: {result}")
    else:
        print(f"Found {len(result)} records")
    ```

=== ":fontawesome-solid-cog:{ .middle } &nbsp; Error Models"

    ```python linenums="1" hl_lines="6-9"
    from toolfront import Browser
    from pydantic import BaseModel

    browser = Browser("file://path/to/mysite")

    class BrowserError(BaseModel):
        error_type: str
        message: str
        suggestion: str

    # Handle both success and error cases
    result: list[dict] | BrowserError = browser.ask("Complex operation")
    # Returns: list[dict] or BrowserError

    if isinstance(result, BrowserError):
        print(f"Error: {result.message} | Suggestion: {result.suggestion}")
    ```

=== ":fontawesome-solid-shield-alt:{ .middle } &nbsp; Output Validation"

    ```python linenums="1" hl_lines="6-13"
    from toolfront import Browser
    from pydantic import BaseModel, Field, validator

    browser = Browser("file://path/to/mysite")

    class Customer(BaseModel):
        name: str = Field(..., min_length=1)
        email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
        age: int = Field(..., ge=0, le=120)

        @validator('email')
        def validate_email(cls, v):
            return v.lower()

    # Pydantic automatically validates responses
    customers: list[Customer] = browser.ask("Get all customers")
    ```

</div>

---

## MCP Server

The Browser MCP server enables AI agents to navigate environments and execute tools through the Model Context Protocol.
