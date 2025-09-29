---
hide:
  - title
  - header
  - footer
  - navigation
  - toc
---

<center>
<h1 style="font-size: 40px">
  <b>Data retrieval environments for AI</b>
</h1>
</center>

<!-- 
<div class="grid header" style="padding-top: 10%; padding-bottom: 10%;" markdown>

<div style="padding-right: 5%;" markdown>


<h1 style="font-size: 40px">
  <b>Data retrieval environments for AI</b>
</h1>

<h2>Turn your markdowns and scripts into interactive sites for your AI agents.</h2>


[Quickstart](#quickstart){ .md-button .md-button--primary }
[Learn more](documentation/browser.md){ .md-button .md-button--secondary }

</div>


<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-code-branch:{ .middle } &nbsp; Environments"

    ```bash
    toolsite/
    ├── index.md
    ├── database/
    │   ├── script.py
    │   └── index.md
    └── documents/
        ├── script.rs
        └── index.md
    ```

=== ":fontawesome-brands-markdown:{ .middle } &nbsp; Markdowns"

    ```markdown
    ---
    [python3, hello.py]
    ---

    # My toolsite

    You are a business analyst. Your goal is to answer user question.
    Run `hello.py` to be greeted by a welcome message!
    ```

=== ":fontawesome-solid-code:{ .top } &nbsp; Scripts"

    ```python
    import click

    @click.command()
    @click.option('--region', help='Sales region to analyze')
    def sales_report(region):
        """Generate sales report for a region"""
        total = 45000 if region == 'north' else 38000
        click.echo(f"Sales in {region}: ${total}")
    ```

=== ":fontawesome-solid-globe:{ .top } &nbsp; Browse"

    ```python
    from toolfront import Browser

    browser = Browser("file://path/to/mysite")

    model = "openai:gpt-5"

    answer = browser.ask("What are my top sellers?", model=model)
    print(answer)
    ```
    
</div>

</div>

<br>

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

## **It's just markdown** {#quickstart}

Each `.md` file defines your AI agent's instructions and the CLI commands it can run on that page.

[Learn More](documentation/ai_models/openai.md){ .md-button .md-button--secondary }

</div>

## Environment



<div class="tabbed-set" markdown="1">


=== ":fontawesome-brands-markdown:{ .middle } &nbsp; Instructions"

    ```markdown hl_lines="5-14"
    ---
    [python3, main.py]
    ---

    # My toolsite

    You are a business analyst. Your goal is to answer the user's quesiton.

    Run `main.py` to retrieve the latest orders.

    Go to ./page_1 to learn about our products.
    Go to ./page_2 to learn about our customers.
    ```

=== ":fontawesome-solid-terminal:{ .middle } &nbsp; Tools"

    ```markdown hl_lines="1-3"
    ---
    [python3, main.py]
    ---

    # My toolsite

    You are a business analyst. Your goal is to answer the user's quesiton.

    Run `main.py` to retrieve the latest orders.

    Go to ./page_1 to learn about our products.
    Go to ./page_2 to learn about our customers.
    ```

</div>

</div>


<div class="main-container-right" markdown>

<div class="tabbed-set" markdown="1">


=== ":fontawesome-solid-cube:{ .middle } &nbsp; Primitives"


    ```python
    from toolfront import Browser

    browser = Browser(model="openai:gpt-5")

    best_seller: str = browser.ask("What's our best-seller?")
    # Returns: "Laptop Pro"

    total_orders: int = browser.ask("How many orders do we have?")
    # Returns: 125

    has_inventory: bool = browser.ask("Do we have pending refunds?")
    # Returns: True
    ```


=== ":fontawesome-solid-layer-group:{ .middle } &nbsp; Collections"

    ```python
    from toolfront import Browser

    browser = Browser("https://api.company.com/docs")

    monthly_sales: list[int] = browser.ask("Monthly sales this year?")
    # Returns: [15000, 18000, 22000]

    sales_by_region: dict[str, int] = browser.ask("Sales by region?")
    # Returns: {"North": 45000, "South": 38000}

    unique_brands: set[str] = browser.ask("What brands do we carry?")
    # Returns: {"Apple", "Dell", "HP"}
    ```

=== ":fontawesome-solid-chain:{ .middle } &nbsp; Unions"

    ```python
    from toolfront import Browser

    browser = Browser("s3://analytics-bucket/reports")

    price: int | float = browser.ask("Price of product XYZ?")
    # Returns: 30 or 29.99

    result: list[str] | str = browser.ask("Best-sellers this month?")
    # Returns: ["Product A", "Product B"] or "Product C"

    error: str | None = browser.ask("What was the error message?")
    # Returns: "Connection timeout" or None
    ```

=== ":fontawesome-solid-sitemap:{ .middle } &nbsp; Pydantic Objects"

    ```python
    from toolfront import Browser
    from pydantic import BaseModel

    browser = Browser("git://github.com/company/invoandices")

    class Customer(BaseModel):
        name: str
        seats: int
        is_active: bool

    top_customer: Customer = browser.ask("Who's our latest customer?")
    # Returns: Customer(name='Acme', seats=5, is_active=True)
    ```


</div>

<div class="grid-item-text" markdown>

## **Browse like the web**

Use your LLM to browse browse environments and retrieve data in the format you need.

[Learn more](documentation/browser.md){ .md-button .md-button--secondary }

</div>

</div>

<div class="main-container-left" markdown>

<div class="grid-item-text" markdown>

## **Host it anywhere** {#quickstart}

Write CLI tools in any language, or use toolfront's built commands for documents and databases.

[Learn More](documentation/ai_models/openai.md){ .md-button .md-button--secondary }

</div>

<div class="tabbed-set" markdown="1">

=== ":fontawesome-brands-python:{ .middle } &nbsp; Filesystem"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser("file://path/to/toolsite")

    model = "openai:gpt-5"

    answer = browser.ask("What are my top sellers?", model=model)
    print(answer)
    ```

=== ":simple-rust:{ .middle } &nbsp; S3"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser(
        "s3://bucket",
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY",
        region_name="us-east-1"
    )

    model = "openai:gpt-5"

    answer = browser.ask("What are my top sellers?", model=model)
    print(answer)
    ```
=== ":simple-rust:{ .middle } &nbsp; S3"

    ```python linenums="1"
    from toolfront import Browser

    browser = Browser(
        "s3://bucket",
        aws_access_key_id="YOUR_ACCESS_KEY",
        aws_secret_access_key="YOUR_SECRET_KEY",
        region_name="us-east-1"
    )

    model = "openai:gpt-5"

    answer = browser.ask("What are my top sellers?", model=model)
    print(answer)
    ```

</div>

</div> -->