"""
Basic PDF invoice extraction example using ToolFront.

NOTE: This is a BASIC example demonstrating simple invoice extraction.
It has NOT been tested for complex scenarios like:
- Extracting data from 1000+ page PDFs
- Finding every person mentioned across a large document
- Processing scanned or low-quality PDFs
"""
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from toolfront import Document

load_dotenv()


class Invoice(BaseModel):
    """Structured invoice data model."""
    invoice_number: str = Field(description="Invoice number (e.g., INV-001)")
    vendor_name: str = Field(description="Company/person who sent the invoice")
    client_name: str = Field(description="Company/person being billed")
    total_amount: float = Field(description="Total amount due (just the number)")
    currency: str = Field(default="USD", description="Currency code")
    due_date: str = Field(description="Due date in YYYY-MM-DD format")
    line_items: list[str] = Field(default=[], description="List of products/services")


def extract_invoice_data(pdf_path: str) -> Invoice:
    """Extract structured invoice data from PDF."""
    doc = Document(filepath=pdf_path)
    
    invoice: Invoice = doc.ask("Extract all invoice information from this PDF", model="anthropic:claude-3-5-sonnet-latest")

    return invoice


if __name__ == "__main__":
    sample_pdf = Path(__file__).parent / "sample-invoice.pdf"

    if not sample_pdf.exists():
        print("Downloading sample invoice PDF...")
        import requests
        url = "https://github.com/excid3/receipts/raw/main/examples/invoice.pdf"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        sample_pdf.write_bytes(response.content)
        print(f"✓ Downloaded sample to {sample_pdf}\n")

    print("🧾 Processing invoice PDF...")
    
    try:
        invoice = extract_invoice_data(str(sample_pdf))
        print("✅ Invoice processed successfully!")
        print(f"\nInvoice: {invoice.invoice_number}")
        print(f"Vendor: {invoice.vendor_name}")
        print(f"Customer: {invoice.client_name}")
        print(f"Amount: {invoice.currency} {invoice.total_amount}")
        print(f"Due Date: {invoice.due_date}")
        print(f"Items: {', '.join(invoice.line_items) if invoice.line_items else 'N/A'}")
    except Exception as e:
        print(f"❌ Failed: {e}")
