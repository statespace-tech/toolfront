# Complete Example

In this example, we'll build a sales analytics environment for an e-commerce company, powered by GPT-5. The agent will answer business questions by pulling data from three sources:

- A PostgreSQL database with transaction data
- A REST API for real-time pricing
- Local receipt files stored as JSON documents

---

## 1. Install ToolFront

Start by install ToolFront with PostgreSQL support.

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

Create a directory structure for the sales analytics environment. Each markdown page will provide tools to access a different data source.

```bash
sales-analytics/
├── index.md
├── database/
│   └── index.md
├── api/
│   └── index.md
└── documents/
    ├── index.md
    └── receipts/
        ├── receipt_20240115_001.txt
        ├── receipt_20240118_002.txt
        └── receipt_20240225_003.txt
```

---

## 4. Create the Home Page

The home page serves as the entry point and explains what data is available.

```markdown title="sales-analytics/index.md"
# Sales Analytics Environment

You are a business analyst at an e-commerce company. Answer questions about sales performance, customer behavior, and inventory using company data.

**Important**: Use ONLY data explicitly retrieved through the provided tools. Never make assumptions or use general knowledge.

## Available Resources

- **[Database](./database)** - Query PostgreSQL with sales transactions, product catalog, and customer records
- **[API](./api)** - Fetch real-time pricing and inventory from the product management API
- **[Documents](./documents)** - Read customer receipts

## Guidelines

1. Read the user's question carefully
2. Navigate to the appropriate page based on what data you need
3. Use the tools on that page to retrieve the data
4. Return answers based only on retrieved data
```

---

## 5. Create the Database Page

Define tools for querying PostgreSQL.

```markdown title="sales-analytics/database/index.md"
---
tools:
  - [toolfront, database, list-tables]
  - [toolfront, database, inspect-table]
  - [toolfront, database, query]
---

# Database

Query the sales database for transaction history, product details, and customer information.

## Available Tables

- `transactions` - Sales transactions with dates, amounts, and product IDs
- `products` - Product catalog with names, categories, and current inventory
- `customers` - Customer records with demographics and contact information

## Instructions

1. Use `list-tables` to see all available tables
2. Use `inspect-table` to understand table structure and columns
3. Use `query` to run SQL queries and retrieve data

Always verify table structure before writing queries.
```

---

## 6. Create the API Page

Provide access to real-time data from an external product management system.

```markdown title="sales-analytics/api/index.md"
---
tools:
  - [curl, -X, GET, "https://api.products.com/v1/pricing"]
  - [curl, -X, GET, "https://api.products.com/v1/inventory/warehouse-01"]
  - [curl, -X, GET, "https://api.products.com/v1/promotions/active"]
---

# Product API

Fetch current pricing and inventory data from the external product management system.

## Available Endpoints

- **GET /v1/pricing** - Current pricing for all products
- **GET /v1/inventory/warehouse-01** - Real-time warehouse inventory
- **GET /v1/promotions/active** - Active promotional campaigns

## Instructions

1. Use curl commands to make API requests
2. API returns JSON responses with product data
3. Combine API data with database records when needed

The API provides the most up-to-date pricing and inventory information.
```

---

## 7. Create the Documents Page

Describe the file structure and formats. The browser handles file reading and searching.

```markdown title="sales-analytics/documents/index.md"
# Documents

Customer receipts are stored as plain text files in the documents directory.

## Available Files

**Receipts** (in `receipts/`)

Receipt filenames indicate transaction dates (e.g., `receipt_20240115_001.txt` is from January 15, 2024).

## File Format

Receipts are plain text files containing:

- Receipt ID and transaction timestamp
- Store location and ID
- Customer details (name, email, member ID)
- Line items with SKUs, product names, quantities, prices, and discounts
- Subtotals, tax, and totals
- Payment method

## Notes

These documents contain detailed transaction-level data not available in the database, including customer emails and SKU-level pricing details.
```

---

## 8. Add Sample Documents

Lastly, add sample receipts under `receipts/` to complete the environment.

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

Initialize a browser and ask questions. The agent will navigate to the appropriate pages and uses the available tools to answer questiosn in the format you specify.

```python
from toolfront import Browser

# Configure browser with model and database credentials
browser = Browser(
    model="openai:gpt-5",
    env={"POSTGRES_URL": "postgres://user:pass@localhost:5432/salesdb"}
)

url = "file:///path/to/sales-analytics"

# Get string as reponse
answer = browser.ask(
    "What was the total for receipt RCP-2024-001?",
    url=url
)

# Get a list of floats as response
products = browser.ask(
    "What is the tax amount paid by our latest customers?"
    url=url,
    output_type=list[float]
)
```

!!! tip "Environment Variables"
    Database credentials are passed through the `env` parameter. The agent can reference environment variable names like `$POSTGRES_URL` when calling tools but never sees the actual values.

---

## 10. Use Structured Output

Specify output types to get structured objects.

```python
from pydantic import BaseModel, Field

class SalesReport(BaseModel):
    total_revenue: float = Field(description="Total revenue in USD")
    units_sold: int = Field(description="Total units sold")
    top_product: str = Field(description="Best-selling product name")
    avg_transaction: float = Field(description="Average transaction value")

report = browser.ask(
    "Generate a sales report combining database transactions and receipts",
    url=url,
    output_type=SalesReport
)

print(f"Revenue: ${report.total_revenue}")
print(f"Top Product: {report.top_product}")
```
