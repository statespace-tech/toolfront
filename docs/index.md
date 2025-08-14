---
hide:
  - title
  - header
  - footer
  - navigation
  - toc
---

<div class="grid header" style="padding-top: 10%; padding-bottom: 10%;" markdown>

<div style="padding-right: 5%;" markdown>


<h1 style="font-size: 40px">
  <b>Data retrieval for AI agents</b>
</h1>

<h2>Simple, open-source data retrieval with unmatched control, precision, and speed.</h2>


[Quickstart](#quickstart){ .md-button .md-button--primary }
[Learn more](documentation/retrieval.md){ .md-button .md-button--secondary }

</div>

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-database:{ .middle } &nbsp; Databases"

    ```python
    from toolfront import Database

    # Connect +10 databases and warehouses
    db = Database("postgres://user:pass@localhost:5432/mydb")

    answer = db.ask("What's the revenue of our top-5 products")
    print(answer)
    ```

=== ":fontawesome-solid-code:{ .top } &nbsp; APIs"

    ```python
    from toolfront import API

    # Connect any API with a spec
    api = API("http://localhost:8000/openapi.json")

    answer = api.ask("Get the latest ticket for user_id=42")
    print(answer)
    ```

=== ":fontawesome-solid-file:{ .top } &nbsp; Documents"

    ```python
    from toolfront import Document

    # Connect any document
    doc = Document("/path/annual_report.pdf")

    answer = doc.retrieve("What were the montlhly payments?")
    print(answer)
    ```

</div>

</div>

<br>

<h2 align="center"><b>Bring your data and LLM.</b></h2>

<div class="db-marquee">
  <div class="db-marquee-track">
    <div class="db-marquee-item" data-db="postgresql">
      <img src="assets/img/databases/postgres.svg" alt="PostgreSQL" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="mysql">
      <img src="assets/img/databases/mysql.svg" alt="MySQL" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="sqlite">
      <img src="assets/img/databases/sqlite.svg" alt="SQLite" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="snowflake">
      <img src="assets/img/databases/snowflake.svg" alt="Snowflake" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="bigquery">
      <img src="assets/img/databases/bigquery.svg" alt="BigQuery" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="databricks">
      <img src="assets/img/databases/databricks.svg" alt="Databricks" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="duckdb">
      <img src="assets/img/databases/duckdb.svg" alt="DuckDB" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="postgresql">
      <img src="assets/img/databases/supabase.svg" alt="Supabase" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="oracle">
      <img src="assets/img/databases/oracle.svg" alt="Oracle" class="db-marquee-icon">
    </div>
    <div class="db-marquee-item" data-db="mssql">
      <img src="assets/img/databases/mssql.svg" alt="SQL Server" class="db-marquee-icon">
    </div>
  </div>
</div>


<div class="models-marquee">
  <div class="models-marquee-track">
    <div class="models-marquee-item" data-model="openai">
      <img src="assets/img/models/chatgpt.svg" alt="ChatGPT" class="models-marquee-icon">
    </div>
    <div class="models-marquee-item" data-model="anthropic">
      <img src="assets/img/models/claude.svg" alt="Claude" class="models-marquee-icon">
    </div>
    <div class="models-marquee-item" data-model="google">
      <img src="assets/img/models/gemini.svg" alt="Gemini" class="models-marquee-icon">
    </div>
    <div class="models-marquee-item" data-model="mistral">
      <img src="assets/img/models/mistral.svg" alt="Mistral" class="models-marquee-icon">
    </div>
    <div class="models-marquee-item" data-model="xai">
      <img src="assets/img/models/xai.svg" alt="xAI Grok" class="models-marquee-icon">
    </div>
    <div class="models-marquee-item" data-model="huggingface">
      <img src="assets/img/models/huggingface.svg" alt="Hugging Face" class="models-marquee-icon">
    </div>
    <div class="models-marquee-item" data-model="deepseek">
      <img src="assets/img/models/deepseek.svg" alt="DeepSeek" class="models-marquee-icon">
    </div>
    <div class="models-marquee-item" data-model="groq">
      <img src="assets/img/models/groq.svg" alt="Groq" class="models-marquee-icon">
    </div>
  </div>
</div>

<br>

<div class="main-container-left" markdown>

<div class="grid-item-text" markdown>

## **Zero Configuration** {#quickstart}

Skip config files and infrastructure setup. ToolFront works out of the box with all your data and models.

[Learn More](documentation/ai_models/openai.md){ .md-button .md-button--secondary }

</div>

<div class="tabbed-set" markdown="1">

<!-- === ":fontawesome-solid-download:{ .middle } &nbsp; pip"
    ```bash
    pip install "toolfront[postgres]"
    ```

    === "OpenAI"
        ```bash
        export OPENAI_API_KEY=<YOUR-KEY>
        ```

        <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

        ```python
        Database("postgres://...", model="openai:gpt-4o")
        ```

    === "Anthropic"
        ```bash
        export ANTHROPIC_API_KEY=<YOUR-KEY>
        ```

        <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

        ```python
        Database("postgres://...", model="anthropic:claude-3-5-sonnet")
        ```


=== ":simple-uv:{ .middle } &nbsp; uv"
    ```bash
    pip install "toolfront[postgres]"
    ```

    === "OpenAI"
        ```bash
        export OPENAI_API_KEY=<YOUR-KEY>
        ```

    === "Anthropic"
        ```bash
        export ANTHROPIC_API_KEY=<YOUR-KEY>
        ``` -->

=== ":fontawesome-solid-download:{ .middle } &nbsp; pip"

    ```bash
    pip install "toolfront[postgres]"
    ```

    <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

    ```bash
    export OPENAI_API_KEY=<YOUR-KEY>
    ```

    <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

    ```python
    Database("postgres://...", model="openai:gpt-4o")
    ```

=== ":simple-uv:{ .middle } &nbsp; uv"

    ```bash
    uv add "toolfront[snowflake]"
    ```

    <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

    ```bash
    export ANTHROPIC_API_KEY=<YOUR-KEY>
    ```

    <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

    ```python
    Database("snowflake://...", model="anthropic:claude-3-5-sonnet")
    ```

=== ":simple-poetry:{ .middle } &nbsp; poetry"

    ```bash
    poetry add "toolfront[bigquery]" 
    ```

    <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

    ```bash
    export GOOGLE_API_KEY=<YOUR-KEY>
    ```

    <center>:material-arrow-down:{ style="font-size: 24px;" }</center>

    ```python
    Database("bigquery://...", model="google:gemini-pro")
    ```

</div>

</div>

<div class="main-container-right" markdown>

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-cube:{ .middle } &nbsp; Primitives"

    ```python
    from toolfront import Database

    db = Database("postgres://user:pass@host/db")

    best_seller: str = db.ask("What's our best-seller?")
    # Returns: "Laptop Pro"

    total_orders: int = db.ask("How many orders do we have?")
    # Returns: 125

    has_inventory: bool = db.ask("Do we have pending refunds?")
    # Returns: True
    ```


=== ":fontawesome-solid-layer-group:{ .middle } &nbsp; Collections"

    ```python
    from toolfront import Database

    db = Database("mysql://user:pass@host/ecommerce")

    monthly_sales: list[int] = db.ask("Monthly sales this year?")
    # Returns: [15000, 18000, 22000]

    sales_by_region: dict[str, int] = db.ask("Sales by region?")
    # Returns: {"North": 45000, "South": 38000}

    unique_brands: set[str] = db.ask("What brands do we carry?")
    # Returns: {"Apple", "Dell", "HP"}
    ```

=== ":fontawesome-solid-chain:{ .middle } &nbsp; Unions"

    ```python
    from toolfront import API

    api = API("https://api.example.com/openapi.json")

    price: int | float = api.ask("Price of product XYZ?")
    # Returns: 30 or 29.99

    result: list[str] | str = api.ask("Best-sellers this month?")
    # Returns: ["Product A", "Product B"] or "Product C"

    error: str | None = api.ask("What was the error message?")
    # Returns: "Connection timeout" or None
    ```


=== ":fontawesome-solid-sitemap:{ .middle } &nbsp; Pydantic Objects"

    ```python
    from toolfront import Document
    from pydantic import BaseModel

    doc = Document("/path/to/invoice.pdf")

    class Customer(BaseModel):
        name: str
        seats: int
        is_active: bool

    top_customer: Customer = doc.ask("Who's our latest customer?")
    # Returns: Customer(name='Acme', seats=5, is_active=True)
    ```

</div>

<div class="grid-item-text" markdown>

## **Predictable Results**

Data is messy. ToolFront returns structured, type-safe responses that match exactly what you want.

[Learn more](documentation/retrieval.md){ .md-button .md-button--secondary }

</div>

</div>

<div class="main-container-left" markdown>

<div class="grid-item-text" markdown>

## **Use it Anywhere**

Avoid migrations. Run ToolFront directly, as an MCP server, or build custom tools for any AI framework.

[Learn more](documentation/mcp.md){ .md-button .md-button--secondary }


</div>

<div class="tabbed-set" markdown="1">

=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": [
            "toolfront[postgres]", 
            "postgres://user:pass@host/db"
          ]
        }
      }
    }
    ```

=== ":fontawesome-solid-wrench:{ .middle } &nbsp; Custom Tools"

    ```python
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    def get_data(query: str):
        """Get data from the database."""
        context = "Sales data is in `orders` table. Revenue in USD."
        return db.ask(query, context=context)

    # Use this function as a tool in any framework
    tools = [get_data]
    ```

</div>

</div>
