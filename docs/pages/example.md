# Example: Sales Analytics

In this example, you'll learn how to build a sales analytics application where an AI agent (OpenAI's GPT-5) answers business questions by querying a PostgreSQL database, calling REST APIs, and reading receipt files.

---

## 1. Install ToolFront

Install ToolFront.

```bash
pip install toolfront
```

---

## 2. Configure Your AI Model

Set your OpenAI API key to use GPT-5.

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

---

## 3. Create Your Project Structure

Create a directory structure with a Markdown page for every data source.

```bash
sales-analytics/
├── README.md
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

## 4. Create the Entry Point

Create `README.md` as the home page with instructions and navigation tools.

```markdown title="sales-analytics/README.md"
---
tools:
  - [ls]
  - [cat]

---

# Sales Analytics

You are a business analyst at an e-commerce company.
Answer questions about sales performance, customer behavior,
and inventory using company data.

**Important**: Use ONLY data explicitly retrieved through
the provided tools. Never make assumptions or use general knowledge.

## Available Pages

- [Database](./pages/database.md) - User accounts and profiles
- [API](./pages/api.md) - Product catalog and inventory
- [Documents](./pages/documents.md) - Transaction receipts

## Instructions

1. Read the user's question carefully
2. Navigate to the appropriate page based on what data you need
3. Use the tools on the page to retrieve the data
```

---

## 5. Create the Database Page

Create `pages/database.md` with tools for querying PostgreSQL.

```markdown title="sales-analytics/pages/database.md"
---
tools:
  - [psql, -U, $USER, -d, $DATABASE, -c, {query}]

---

# Database

Query the PostgreSQL database for user accounts and profile information.

## Available Tables

- `users` - User accounts with emails and registration dates
- `profiles` - User profiles with names and preferences

## Instructions

1. Pass SQL queries using the `{query}` placeholder
2. Start with `SELECT * FROM users LIMIT 5;` to explore data
3. Join `users` and `profiles` for complete customer information
```

---

## 6. Create the API Page

Create `pages/api.md` with tools for fetching product data from a REST API.

```markdown title="sales-analytics/pages/api.md"
---
tools:
  - [curl, -X, GET, "https://api.products.com/{endpoint}"]

---

# Product API

Fetch product catalog and inventory data from the product management system.

## Available Endpoints

- `v1/categories` - Product categories
- `v1/products?category=<category_name>` - Products in a category
- `v1/inventory?sku=<product_sku>` - Current inventory levels for a product

## Instructions

1. Pass the `{endpoint}` parameter to make API requests
2. Include query parameters in the endpoint as needed
3. API returns JSON with product data
```

---

## 7. Create the Documents Page

Create `pages/documents.md` describing the receipt file structure for agents to read.

```markdown title="sales-analytics/pages/documents.md"
---
tools:
  - [grep]

---

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

1. Use `grep` to search through receipts in `../data/receipts/`
2. Search by transaction ID, customer name, SKU, or date
3. Read individual files for complete transaction details
```

---

## 8. Add Sample Receipts

Add sample receipt files in `data/receipts/` for the agent to analyze.

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

## 9. Run Your Application

Use the Python SDK to load and interact with your application.

```python
from toolfront import Application

# Initialize application
app = Application(url="file:///path/to/sales-analytics")

# Get string as response
answer = app.run(
    prompt="What was the total for receipt RCP-2024-001?",
    model="openai:gpt-5"
)

# Get a list of floats as response
taxes = app.run(
    prompt="What is the tax amount paid by our latest customers?",
    model="openai:gpt-5",
    output_type=list[float]
)
```

---

## 10. Get Structured Output

Use Pydantic models to retrieve structured data from your application.

```python
from pydantic import BaseModel, Field

class SalesReport(BaseModel):
    total_revenue: float = Field(description="Total revenue in USD")
    units_sold: int = Field(description="Total units sold")
    top_product: str = Field(description="Best-selling product name")
    avg_transaction: float = Field(description="Average transaction value")

report = app.run(
    prompt="Generate a sales report from all receipts",
    model="openai:gpt-5",
    output_type=SalesReport
)

print(f"Revenue: ${report.total_revenue}")
print(f"Top Product: {report.top_product}")
```

---

You now have a complete sales analytics application! The agent can navigate between pages, query databases, call APIs, and analyze documents to answer complex business questions.
