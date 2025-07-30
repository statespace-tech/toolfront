"""
Complete Invoice Processing Workflow with ToolFront

This example shows how PDF extraction fits into a larger business process:
1. Extract invoice data from PDFs
2. Validate business rules
3. Save to database/CSV
4. Generate processing reports
5. Move files to appropriate folders

Perfect for demonstrating automated invoice processing to customers.
"""

import csv
import shutil
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

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


class ProcessingResult(BaseModel):
    """Result of processing a single invoice."""

    filename: str
    status: str  # "success", "failed", "validation_error"
    invoice: Invoice | None = None
    error_message: str | None = None
    processed_at: datetime = Field(default_factory=datetime.now)


class InvoiceProcessor:
    """Complete invoice processing workflow."""

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        (self.output_dir / "processed").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "failed").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "reports").mkdir(parents=True, exist_ok=True)

    def extract_invoice_data(self, pdf_path: Path) -> Invoice:
        """Extract structured invoice data from PDF using ToolFront."""
        doc = Document(source=str(pdf_path))

        invoice: Invoice = doc.ask(
            """
            Extract complete invoice information from this PDF:
            - Invoice number (look for invoice #, inv #, etc.)
            - Vendor name (who sent this invoice)
            - Client name (who is being billed)
            - Total amount (final amount to be paid, just the number)
            - Currency (USD, EUR, etc. - default to USD if unclear)
            - Due date (when payment is due, format as YYYY-MM-DD)
            - Line items (products or services being charged for)
            
            Be precise and only extract data that is clearly visible.
        """,
            model="anthropic:claude-3-5-sonnet-latest",
        )

        return invoice

    def validate_invoice(self, invoice: Invoice) -> tuple[bool, str | None]:
        """Apply business rules validation."""
        # Example business rules
        if invoice.total_amount <= 0:
            return False, "Invoice amount must be positive"

        if invoice.total_amount > 100000:
            return False, "Invoice amount exceeds $100,000 limit - requires manual review"

        if not invoice.invoice_number.strip():
            return False, "Invoice number is required"

        # Check for suspicious patterns (very basic - customize for your needs)
        suspicious_vendors = ["suspicious_vendor", "fake_company"]
        if any(word in invoice.vendor_name.lower() for word in suspicious_vendors):
            return False, f"Suspicious vendor name: {invoice.vendor_name}"

        return True, None

    def process_single_pdf(self, pdf_path: Path) -> ProcessingResult:
        """Process a single PDF file."""
        try:
            invoice = self.extract_invoice_data(pdf_path)

            is_valid, validation_error = self.validate_invoice(invoice)
            if not is_valid:
                return ProcessingResult(
                    filename=pdf_path.name, status="validation_error", error_message=validation_error
                )

            processed_path = self.output_dir / "processed" / pdf_path.name
            shutil.copy2(pdf_path, processed_path)

            return ProcessingResult(filename=pdf_path.name, status="success", invoice=invoice)

        except ValidationError as e:
            return ProcessingResult(
                filename=pdf_path.name, status="validation_error", error_message=f"Pydantic validation error: {str(e)}"
            )
        except Exception as e:
            failed_path = self.output_dir / "failed" / pdf_path.name
            shutil.copy2(pdf_path, failed_path)

            return ProcessingResult(filename=pdf_path.name, status="failed", error_message=str(e))

    def process_batch(self, pdf_files: list[Path]) -> list[ProcessingResult]:
        """Process multiple PDF files."""
        results = []

        print(f"📄 Processing {len(pdf_files)} PDF files...")

        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"Processing {i}/{len(pdf_files)}: {pdf_path.name}")
            result = self.process_single_pdf(pdf_path)
            results.append(result)

            if result.status == "success":
                print(f"  ✅ Success - {result.invoice.vendor_name} - ${result.invoice.total_amount}")
            else:
                print(f"  ❌ {result.status}: {result.error_message}")

        return results

    def save_to_csv(self, results: list[ProcessingResult], filename: str = "invoices.csv"):
        """Save successful extractions to CSV for accounting system import."""
        csv_path = self.output_dir / "reports" / filename

        successful_results = [r for r in results if r.status == "success" and r.invoice]

        if not successful_results:
            print("No successful invoices to save.")
            return

        with csv_path.open("w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "invoice_number",
                "vendor_name",
                "client_name",
                "total_amount",
                "currency",
                "due_date",
                "line_items_count",
                "filename",
                "processed_at",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in successful_results:
                inv = result.invoice
                writer.writerow(
                    {
                        "invoice_number": inv.invoice_number,
                        "vendor_name": inv.vendor_name,
                        "client_name": inv.client_name,
                        "total_amount": inv.total_amount,
                        "currency": inv.currency,
                        "due_date": inv.due_date,
                        "line_items_count": len(inv.line_items),
                        "filename": result.filename,
                        "processed_at": result.processed_at.isoformat(),
                    }
                )

        print(f"💾 Saved {len(successful_results)} invoices to {csv_path}")

    def generate_report(self, results: list[ProcessingResult]) -> str:
        """Generate processing summary report."""
        total = len(results)
        successful = len([r for r in results if r.status == "success"])
        failed = len([r for r in results if r.status == "failed"])
        validation_errors = len([r for r in results if r.status == "validation_error"])

        successful_invoices = [r.invoice for r in results if r.status == "success" and r.invoice]
        total_amount = sum(inv.total_amount for inv in successful_invoices)

        avg_invoice = total_amount / len(successful_invoices) if successful_invoices else 0

        report = f"""
📊 INVOICE PROCESSING REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📈 SUMMARY:
• Total files processed: {total}
• Successfully extracted: {successful} ({successful / total * 100:.1f}%)
• Failed extractions: {failed}
• Validation errors: {validation_errors}

💰 FINANCIAL SUMMARY:
• Total invoice value: ${total_amount:,.2f}
• Average invoice: ${avg_invoice:.2f}

📁 OUTPUT LOCATIONS:
• Processed PDFs: {self.output_dir}/processed/
• Failed PDFs: {self.output_dir}/failed/
• CSV export: {self.output_dir}/reports/invoices.csv
"""

        report_path = self.output_dir / "reports" / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.write_text(report)

        return report


def demo_workflow():
    """Demonstrate the complete invoice processing workflow."""
    input_dir = Path("examples")
    output_dir = Path("examples/output")

    sample_pdf = input_dir / "sample-invoice.pdf"
    if not sample_pdf.exists():
        print("Downloading sample invoice PDF...")
        import requests

        url = "https://github.com/excid3/receipts/raw/main/examples/invoice.pdf"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        sample_pdf.write_bytes(response.content)
        print(f"✓ Downloaded sample to {sample_pdf}")

    processor = InvoiceProcessor(input_dir, output_dir)

    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in examples directory.")
        return

    results = processor.process_batch(pdf_files)

    processor.save_to_csv(results)

    report = processor.generate_report(results)
    print(report)

    print("\n🎉 Workflow complete! Check the output directory for results.")


if __name__ == "__main__":
    demo_workflow()
