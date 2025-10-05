# Complete Example

In this example, we'll build a sales analytics environment for an e-commerce company. We'll use GPT-5 to answer business questions by pulling data from three sources: a PostgreSQL database with transaction history, a REST API for real-time pricing, and local receipt files stored as JSON documents.

The agent will automatically navigate between pages to find the right data for each question.

---

## 1. Install ToolFront

Install ToolFront with PostgreSQL support.

```bash
pip install "toolfront[postgres]"
```

---

## 2. Configure GPT-5

Set your OpenAI API key to use GPT-5.

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

---

## 3. Set Up Your Environment

Create a directory structure for the sales analytics environment. Each markdown page provides access to a different data source.

```bash
sales-analytics/
├── index.md
├── database/
│   └── index.md
├── api/
│   └── index.md
└── documents/
    ├── index.md
    ├── receipts/
    │   ├── 2024/
    │   │   ├── january/
    │   │   │   ├── receipt_20240115_001.json
    │   │   │   └── receipt_20240118_002.json
    │   │   └── february/
    │   └── archive/
    └── reports/
        └── invoice_summary_jan2024.txt
```

---

## 4. Create the Home Page

The home page serves as the entry point and explains what data is available. Create `sales-analytics/index.md`:

```markdown title="sales-analytics/index.md"
# Sales Analytics Environment

You are a business analyst at an e-commerce company. Your job is to answer questions about sales performance, customer behavior, and inventory using company data.

**Important**: Always use ONLY data explicitly retrieved through the provided tools. Never make assumptions or use general knowledge.

## Available Resources

Navigate to these pages to access different data sources:

- **[Database](./database)** - Query the PostgreSQL database with sales transactions, product catalog, and customer records
- **[API](./api)** - Fetch real-time pricing and inventory from the external product management API
- **[Documents](./documents)** - Read customer receipts and monthly invoice summaries stored as JSON and text files

## Guidelines

1. Read the user's question carefully
2. Navigate to the appropriate page based on what data you need
3. Use the tools on that page to retrieve the data
4. Return answers based only on retrieved data
```

---

## 5. Create the Database Page

The database page defines tools for querying PostgreSQL. Create `sales-analytics/database/index.md`:

```markdown title="sales-analytics/database/index.md"
---
tools:
  - [toolfront, database, list-tables]
  - [toolfront, database, inspect-table]
  - [toolfront, database, query]

---

# Database

Query the sales database to find transaction history, product details, and customer information.

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

The API page provides access to real-time data from an external product management system. Create `sales-analytics/api/index.md`:

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

- **GET /v1/pricing** - Current pricing for all products in catalog
- **GET /v1/inventory/warehouse-01** - Real-time inventory at warehouse location
- **GET /v1/promotions/active** - Active promotional campaigns and discounts

## Instructions

1. Use curl commands to make API requests
2. API returns JSON responses with product data
3. Combine API data with database records when needed

The API provides the most up-to-date pricing and inventory information.
```

---

## 7. Create the Documents Page

The documents page describes the file structure and formats. The browser handles file reading and searching. Create `sales-analytics/documents/index.md`:

```markdown title="sales-analytics/documents/index.md"
# Documents

Customer receipts and financial reports are stored in the documents directory.

## Available Files

**January 2024 Receipts** (in `receipts/2024/january/`)

- `receipt_20240115_001.json` - Downtown Seattle store transaction
- `receipt_20240118_002.json` - Portland Mall store transaction

**Monthly Reports** (in `reports/`)

- `invoice_summary_jan2024.txt` - January 2024 invoice summary report

## File Formats

**Receipts** are JSON files containing:

- Receipt ID and transaction timestamp
- Store location and ID
- Customer details (name, email, member ID)
- Line items with SKUs, product names, quantities, prices, and discounts
- Subtotals, tax, and final totals
- Payment method and card details

**Reports** are plain text files containing:

- Overview with total revenue, invoices, and averages
- Top products by units sold and revenue
- Payment method breakdowns
- Store performance metrics
- Business insights and notes

## Notes

These documents contain detailed transaction-level data not available in the database, including customer emails and SKU-level pricing details.
```

---

## 8. Add Sample Documents

Add sample receipts and reports to complete the environment:

```json title="sales-analytics/documents/receipts/2024/january/receipt_20240115_001.json"
{
  "receipt_id": "RCP-2024-001",
  "transaction_date": "2024-01-15T14:32:18Z",
  "store_location": "Downtown Seattle",
  "store_id": "SEA-001",
  "customer": {
    "name": "John Smith",
    "email": "john.smith@email.com",
    "member_id": "CUST-10234"
  },
  "items": [
    {
      "sku": "LTP-PRO-15",
      "product_name": "Laptop Pro 15-inch",
      "category": "Electronics",
      "quantity": 1,
      "unit_price": 1299.99,
      "discount": 0.00,
      "subtotal": 1299.99
    },
    {
      "sku": "MSE-WRL-BLK",
      "product_name": "Wireless Mouse - Black",
      "category": "Accessories",
      "quantity": 2,
      "unit_price": 29.99,
      "discount": 5.00,
      "subtotal": 54.98
    }
  ],
  "subtotal": 1354.97,
  "tax": 121.95,
  "total": 1476.92,
  "payment_method": "credit_card",
  "card_last_four": "4532"
}
```

```json title="sales-analytics/documents/receipts/2024/january/receipt_20240118_002.json"
{
  "receipt_id": "RCP-2024-002",
  "transaction_date": "2024-01-18T09:15:42Z",
  "store_location": "Portland Mall",
  "store_id": "PDX-003",
  "customer": {
    "name": "Jane Doe",
    "email": "jane.doe@email.com",
    "member_id": "CUST-10891"
  },
  "items": [
    {
      "sku": "CBL-USB-C",
      "product_name": "USB-C Cable 6ft",
      "category": "Accessories",
      "quantity": 3,
      "unit_price": 12.99,
      "discount": 0.00,
      "subtotal": 38.97
    },
    {
      "sku": "LTP-PRO-15",
      "product_name": "Laptop Pro 15-inch",
      "category": "Electronics",
      "quantity": 1,
      "unit_price": 1299.99,
      "discount": 50.00,
      "subtotal": 1249.99
    }
  ],
  "subtotal": 1288.96,
  "tax": 116.01,
  "total": 1404.97,
  "payment_method": "debit_card",
  "card_last_four": "8821"
}
```

```text title="sales-analytics/documents/reports/invoice_summary_jan2024.txt"
MONTHLY INVOICE SUMMARY REPORT
PERIOD: JANUARY 2024
GENERATED: 2024-02-01 09:00:00 PST

===========================================
OVERVIEW
===========================================
Total Invoices Processed: 47
Total Gross Revenue: $45,892.33
Total Tax Collected: $4,130.31
Total Net Revenue: $41,762.02
Average Invoice Value: $976.43

===========================================
TOP PRODUCTS BY UNITS SOLD
===========================================
1. USB-C Cable 6ft (CBL-USB-C) - 56 units
2. Wireless Mouse - Black (MSE-WRL-BLK) - 34 units
3. Laptop Pro 15-inch (LTP-PRO-15) - 12 units
4. Keyboard Mechanical (KBD-MCH-RGB) - 8 units
5. Monitor 27" 4K (MON-27-4K) - 5 units

===========================================
TOP PRODUCTS BY REVENUE
===========================================
1. Laptop Pro 15-inch - $15,599.88
2. Monitor 27" 4K - $2,499.95
3. Wireless Mouse - Black - $1,019.66
4. USB-C Cable 6ft - $727.44
5. Keyboard Mechanical - $719.92

===========================================
PAYMENT METHOD BREAKDOWN
===========================================
Credit Card: 28 invoices ($27,450.12 | 59.8%)
Debit Card: 15 invoices ($14,892.45 | 32.4%)
Cash: 4 invoices ($3,549.76 | 7.7%)

===========================================
STORE PERFORMANCE
===========================================
SEA-001 Downtown Seattle: $18,234.56 (39.7%)
PDX-003 Portland Mall: $15,678.92 (34.2%)
SFO-005 San Francisco: $11,978.85 (26.1%)

===========================================
NOTES
===========================================
- Seattle store showed 23% increase vs December 2023
- Portland Mall experienced highest weekend traffic
- Laptop Pro promotions drove significant revenue
- Monitor inventory running low, restock recommended
```

---

## 9. Query the Environment

Initialize a browser and ask questions. The agent will navigate to the appropriate pages and use the available tools.

```python
from toolfront import Browser

# Configure browser with model and database credentials
browser = Browser(
    model="openai:gpt-5",
    env={"POSTGRES_URL": "postgres://user:pass@localhost:5432/salesdb"}
)

url = "file:///path/to/sales-analytics"

# Ask questions that navigate across different pages
answer = browser.ask(
    "What was our total revenue in January based on the invoice summary?",
    url=url
)

products = browser.ask(
    "List all products sold according to receipts",
    url=url,
    output_type=list[str]
)

# Get structured data from database
top_customers = browser.ask(
    "Who are our top 5 customers by transaction amount?",
    url=url,
    output_type=list[dict]
)
```

---

## 10. Use Structured Output

You can specify output types to get structured data instead of plain text responses.

```python
from pydantic import BaseModel, Field

class SalesReport(BaseModel):
    total_revenue: float = Field(description="Total revenue in USD")
    units_sold: int = Field(description="Total units sold")
    top_product: str = Field(description="Best-selling product name")
    avg_transaction: float = Field(description="Average transaction value")

report = browser.ask(
    "Generate a sales report combining database transactions and document receipts",
    url=url,
    output_type=SalesReport
)

print(f"Revenue: ${report.total_revenue}")
print(f"Top Product: {report.top_product}")
```

!!! tip "Environment Variables"
    Database credentials are passed through the `env` parameter. The agent references variable names like `$POSTGRES_URL` when calling tools, but never sees the actual values.

!!! tip "Navigation"
    The agent follows markdown links to navigate between pages. Each page's instructions help the agent understand what tools are available and when to use them.
