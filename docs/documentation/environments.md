# Quickstart

## Environment

ToolFront turns your markdowns and scripts into interactive sites for your AI agents.

```bash
toolsite/
├── index.md
├── page_1/
│   ├── script.py
│   └── index.md
└── page_2/
    ├── script.rs
    └── index.md
```

---


Each `.md` page can include CLI commands in the frontmatter and instructions in the body.


=== ":fontawesome-solid-terminal:{ .middle } &nbsp; Tools"

    ```markdown hl_lines="1-3"
    ---
    [python3, database/script.py]
    ---

    # Sales Database

    You are a business analyst with access to our sales database.
    Answer questions about revenue, customers, and products.

    ## Available Operations

    - `get_revenue --quarter Q4` - Get quarterly revenue
    - `list_customers --region north` - List customers by region
    - `top_products --limit 10` - Show best-selling products
    ```


=== ":fontawesome-brands-markdown:{ .middle } &nbsp; Instructions"

    ```markdown hl_lines="5-14"
    ---
    [python3, database/script.py]
    ---

    # Sales Database

    You are a business analyst with access to our sales database.
    Answer questions about revenue, customers, and products.

    ## Available Operations

    - `get_revenue --quarter Q4` - Get quarterly revenue
    - `list_customers --region north` - List customers by region
    - `top_products --limit 10` - Show best-selling products
    ```

Agents can take actions by calling CLI command tools, which you can write in any language.

<div class="tabbed-set" markdown="1">

=== ":fontawesome-brands-python:{ .middle } &nbsp; Python"

    ```python title="script.py" linenums="1"
    import click

    @click.command()
    @click.option('--quarter', help='Q1, Q2, Q3, Q4')
    def get_revenue(quarter):
        """Get quarterly revenue."""
        data = fetch_sales_data(quarter)
        total = data.sum()
        click.echo(f"Revenue: ${total:,.2f}")

    if __name__ == '__main__':
        get_revenue()
    ```

=== ":simple-rust:{ .middle } &nbsp; Rust"

    ```rust title="script.rs" linenums="1"
    use clap::Parser;

    #[derive(Parser)]
    struct Args {
        #[arg(short, long)]
        quarter: String,
    }

    fn main() {
        let args = Args::parse();
        let revenue = fetch_sales_data(&args.quarter);
        println!("Revenue: ${:,.2}", revenue);
    }
    ```

</div>

---

## Browsing 

Before launching an agent to browse your environment, export your LLM provider's API key:

<div class="tabbed-set" markdown="1">

=== ":simple-openai:{ .middle } &nbsp; OpenAI"

    ```bash
    export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
    ```

=== ":simple-anthropic:{ .middle } &nbsp; Anthropic"

    ```bash
    export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>
    ```

=== ":simple-google:{ .middle } &nbsp; Google"

    ```bash
    export GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
    ```

</div>

Then, use the Python SDK to launch agents that navigate your environment and find answers to questions:

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-cube:{ .middle } &nbsp; Primitives"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser(model="openai:gpt-4o")

    url = "file:///path/to/toolsite"

    avg_price: float = browser.ask("What's our average ticket price?", url=url)
    # Returns: 29.99

    best_product: str = browser.ask("What's our best-seller?", url=url)
    # Returns: "Laptop Pro"

    has_inventory: bool = browser.ask("Do we have pending refunds?", url=url)
    # Returns: True
    ```

=== ":fontawesome-solid-layer-group:{ .middle } &nbsp; Collections"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser(model="anthropic:claude-3-5-sonnet-latest")

    url = "https://company.com/toolsite"

    monthly_sales: list[int] = browser.ask("Monthly sales this year?", url=url)
    # Returns: [15000, 18000, 22000]

    sales_by_region: dict[str, int] = browser.ask("Sales by region?", url=url)
    # Returns: {"North": 45000, "South": 38000}

    unique_brands: set[str] = browser.ask("What brands do we carry?", url=url)
    # Returns: {"Apple", "Dell", "HP"}
    ```

=== ":fontawesome-solid-chain:{ .middle } &nbsp; Unions"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser(model="google-gla:gemini-2.0-flash-exp")

    url = "s3://analytics-bucket/toolsite"

    price: int | float = browser.ask("Price of product XYZ?", url=url)
    # Returns: 30 or 29.99

    result: list[str] | str = browser.ask("Best-sellers this month?", url=url)
    # Returns: ["Product A", "Product B"] or "Product C"

    error: str | None = browser.ask("What was the error message?", url=url)
    # Returns: "Connection timeout" or None
    ```

=== ":fontawesome-solid-sitemap:{ .middle } &nbsp; Pydantic Objects"

    ```python linenums="1"
    from toolfront import Browser
    from pydantic import BaseModel, Field

    browser = Browser(model="openai:gpt-4o")

    url = "git://github.com/company/toolsite"

    class Customer(BaseModel):
        name: str = Field(..., description="Customer name") # (1)!
        seats: int = Field(..., description="Number of seats")
        is_active: bool = Field(..., description="Customer is active")

    customer: Customer = browser.ask("Who's our best customer?", url=url)
    # Returns: Customer(name='Acme', seats=5, is_active=True)
    ```

    1. Adding Pydantic field descriptions improves retrieval accuracy.

</div>

!!! tip "Alternative: Output Type Parameter"
    You can also specify the output type using the `output_type` parameter:

    ```python
    total_orders = browser.ask("How many orders do we have?", url=..., output_type=int)
    ```

## Hosting

You can host in virtually any filesystem:


