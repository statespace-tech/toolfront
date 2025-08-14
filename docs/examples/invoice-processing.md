# PDF Invoice Processing with Google Gemini

In this example, we'll extract structured invoice data (vendor, amount, due date, line items) from PDF documents using Pydantic models. Google Gemini's large 1M+ token context window makes it ideal for processing complex documents with multiple pages and detailed line items.

## 1. Export your Google API key.

```BASH
export GOOGLE_API_KEY=<YOUR_KEY>
```

## 2. Download a sample invoice to test with.

```bash
curl -o sample-invoice.pdf https://github.com/excid3/receipts/raw/main/examples/invoice.pdf
```

## 3. Extract a structured Pydantic object from the invoice.

```python linenums="1"
from toolfront import Document
from pydantic import BaseModel, Field
from datetime import datetime

class Invoice(BaseModel):
    invoice_number: str = Field(..., description="Invoice number or ID")
    vendor_name: str = Field(..., description="Name of the vendor/supplier company")
    client_name: str = Field(..., description="Name of the client/customer")
    total_amount: float = Field(..., gt=0, lt=100000, description="Total amount due in USD")
    due_date: datetime = Field(..., description="Payment due date")
    line_items: list[str] = Field(..., min_items=1, description="List of invoice line items")

# Extract structured data from PDF
doc = Document("sample-invoice.pdf")
invoice: Invoice = doc.ask(
    "Extract all invoice information from this PDF",
    model="anthropic:claude-3-5-sonnet-latest"
)

print(f"Invoice Number: {invoice.invoice_number}")
print(f"Vendor: {invoice.vendor_name}")
print(f"Client: {invoice.client_name}")
print(f"Amount Due: ${invoice.total_amount}")
print(f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}")
print(f"Line Items: {len(invoice.line_items)} items")

>>> Invoice Number: 123
>>> Vendor: Example, LLC
>>> Client: Customer
>>> Amount Due: $19.0
>>> Due Date: March 25, 2024
>>> Line Items: 1 items
```

!!! tip "Pydantic Fields"
    Use `Field()` with descriptions to improve AI extraction accuracy and validators (`gt=0`, `min_items=1`) to enforce data quality and business rules.