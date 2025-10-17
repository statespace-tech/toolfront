# The Only Example You'll Ever Need

Build a sales analytics environment for an e-commerce company where agents answer business questions by pulling data from a PostgreSQL database, REST API, and local receipt files.

---

## 1. Install ToolFront

Install ToolFront with PostgreSQL support.

```bash
pip install "toolfront[postgres]"
```

---

## 2. Configure AI model

Set your OpenAI API key to use GPT-5.

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

---

## 3. Set Up Your Environment

Create a directory structure with a Markdown page for every data source.

```bash
environment/
├── index.md
├── pages/
│   ├── database.md
│   ├── api.md
│   └── documents.md
└── data/
    └── receipts/
        ├── receipt_20240115_001.txt
        ├── receipt_20240118_002.txt
        └── receipt_20240225_003.txt

4 directories, 7 files
```

---

## 4. Create the Home Page

Create an entry point that explains available data sources and guidelines.

```markdown title="environment/index.md"
# Sales Analytics Environment

You are a business analyst at an e-commerce company.
Answer questions about sales performance, customer behavior,
and inventory using company data.

**Important**: Use ONLY data explicitly retrieved through
the provided tools. Never make assumptions or use general knowledge.

## Available Pages

- [Database](./pages/database.md) - User accounts and profiles
- [API](./pages/api.md) - Product catalog and inventory
- [Documents](./pages/documents.md) - Transaction receipts

## Global Instructions

1. Read the user's question carefully
2. Navigate to the appropriate page based on what data you need
3. Use the tools on the page page to retrieve the data
```

---

## 5. Create the Database Page

Define tools for querying PostgreSQL.

```markdown title="environment/pages/database.md"
---
tools:
  - [toolfront, database, $POSTGRES_URL]

---

# Database

Query the Postgres database for user accounts and profile information.

## Available Tables

- `users` - User accounts with emails and registration dates
- `profiles` - User profiles with names and preferences

## Instructions

1. Use `list-tables` to see available tables
2. Use `inspect-table` to understand structure
3. Use `query` to run SQL and retrieve data
```

---

## 6. Create the API Page

Define tools for fetching real-time data from an external product management API.

```markdown title="environment/pages/api.md"
---
tools:
  - [curl, -X, GET, "https://api.products.com/v1/products"]
  - [curl, -X, GET, "https://api.products.com/v1/inventory"]
  - [curl, -X, GET, "https://api.products.com/v1/categories"]

---

# Product API

Fetch product catalog and inventory data from the product management system.

## Available Endpoints

- `GET /v1/categories` - Product categories
- `GET /v1/products?category=<category_name>` - Products in a category
- `GET /v1/inventory?sku=<product_sku>` - Current inventory levels for a product

## Instructions

1. Use curl to make API requests
2. Append query parameters as needed
3. API returns JSON with product data
```

---

## 7. Create the Documents Page

Describe the file structure and formats for transaction receipts.

```markdown title="environment/pages/documents.md"
# Transaction Receipts

Transaction receipts are stored as plain text files in
the `data/receipts/` directory.

## Available Files

**Receipts** (in `../data/receipts/`)

Receipt filenames indicate transaction dates
(e.g., `receipt_20240115_001.txt` is from January 15, 2024).

## File Format

Receipts are plain text files containing:

- Transaction ID and timestamp
- Store location and ID
- Line items with SKUs, quantities, and prices
- Subtotals, tax, and payment method

## Instructions

1. List files to find receipts by date
2. Read individual files for transaction details
3. Parse receipt data for specific information
```

---

## 8. Add Sample Documents

Add sample receipt files under `data/receipts/` to complete the environment.

=== "receipt_20240115_001.txt"
    ```text
    CUSTOMER RECEIPT
    RECEIPT ID: RCP-2024-001
    DATE: January 15, 2024 at 2:32 PM PST

    ===========================================
    STORE INFORMATION
    ===========================================
    Location: Downtown Seattle
    Store ID: SEA-001

    ===========================================
    CUSTOMER INFORMATION
    ===========================================
    Name: John Smith
    Email: john.smith@email.com
    Member ID: CUST-10234

    ===========================================
    ITEMS PURCHASED
    ===========================================

    1. Laptop Pro 15-inch
       SKU: LTP-PRO-15
       Category: Electronics
       Quantity: 1
       Unit Price: $1,299.99
       Discount: $0.00
       Subtotal: $1,299.99

    2. Wireless Mouse - Black
       SKU: MSE-WRL-BLK
       Category: Accessories
       Quantity: 2
       Unit Price: $29.99
       Discount: $5.00
       Subtotal: $54.98

    ===========================================
    PAYMENT SUMMARY
    ===========================================
    Subtotal: $1,354.97
    Tax (9%): $121.95
    Total: $1,476.92

    Payment Method: Credit Card
    Card: **** **** **** 4532

    ===========================================
    Thank you for shopping with us!
    ```

=== "receipt_20240118_002.txt"
    ```text
    CUSTOMER RECEIPT
    RECEIPT ID: RCP-2024-002
    DATE: January 18, 2024 at 9:15 AM PST

    ===========================================
    STORE INFORMATION
    ===========================================
    Location: Portland Mall
    Store ID: PDX-003

    ===========================================
    CUSTOMER INFORMATION
    ===========================================
    Name: Jane Doe
    Email: jane.doe@email.com
    Member ID: CUST-10891

    ===========================================
    ITEMS PURCHASED
    ===========================================

    1. USB-C Cable 6ft
       SKU: CBL-USB-C
       Category: Accessories
       Quantity: 3
       Unit Price: $12.99
       Discount: $0.00
       Subtotal: $38.97

    2. Laptop Pro 15-inch
       SKU: LTP-PRO-15
       Category: Electronics
       Quantity: 1
       Unit Price: $1,299.99
       Discount: $50.00
       Subtotal: $1,249.99

    ===========================================
    PAYMENT SUMMARY
    ===========================================
    Subtotal: $1,288.96
    Tax (9%): $116.01
    Total: $1,404.97

    Payment Method: Debit Card
    Card: **** **** **** 8821

    ===========================================
    Thank you for shopping with us!
    ```

=== "receipt_20240225_003.txt"
    ```text
    CUSTOMER RECEIPT
    RECEIPT ID: RCP-2024-003
    DATE: February 25, 2024 at 4:47 PM PST

    ===========================================
    STORE INFORMATION
    ===========================================
    Location: San Francisco
    Store ID: SFO-005

    ===========================================
    CUSTOMER INFORMATION
    ===========================================
    Name: Mike Johnson
    Email: mike.j@email.com
    Member ID: CUST-11203

    ===========================================
    ITEMS PURCHASED
    ===========================================

    1. Monitor 27" 4K
       SKU: MON-27-4K
       Category: Electronics
       Quantity: 1
       Unit Price: $499.99
       Discount: $25.00
       Subtotal: $474.99

    2. Keyboard Mechanical RGB
       SKU: KBD-MCH-RGB
       Category: Accessories
       Quantity: 1
       Unit Price: $89.99
       Discount: $0.00
       Subtotal: $89.99

    3. USB-C Cable 6ft
       SKU: CBL-USB-C
       Category: Accessories
       Quantity: 2
       Unit Price: $12.99
       Discount: $0.00
       Subtotal: $25.98

    ===========================================
    PAYMENT SUMMARY
    ===========================================
    Subtotal: $590.96
    Tax (9%): $53.19
    Total: $644.15

    Payment Method: Credit Card
    Card: **** **** **** 9876

    ===========================================
    Thank you for shopping with us!
    ```

---

## 9. Query the Environment

Initialize an environment and ask questions in any output format you need.

```python
from toolfront import Environment

# Initialize environment
environment = Environment(url="file:///path/to/environment")

# Get string as response
answer = environment.run(
    prompt="What was the total for receipt RCP-2024-001?",
    model="openai:gpt-5"
)

# Get a list of floats as response
products = environment.run(
    prompt="What is the tax amount paid by our latest customers?",
    model="openai:gpt-5",
    output_type=list[float]
)
```

---

## 10. Use Structured Output

Use Pydantic models to get structured output objects.

```python
from pydantic import BaseModel, Field

class SalesReport(BaseModel):
    total_revenue: float = Field(description="Total revenue in USD")
    units_sold: int = Field(description="Total units sold")
    top_product: str = Field(description="Best-selling product name")
    avg_transaction: float = Field(description="Average transaction value")

report = environment.run(
    prompt="Generate a sales report combining transactions and receipts",
    model="openai:gpt-5",
    output_type=SalesReport
)

print(f"Revenue: ${report.total_revenue}")
print(f"Top Product: {report.top_product}")
```
