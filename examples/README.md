# ToolFront Examples

This directory contains examples demonstrating ToolFront's capabilities.

## Examples

### 1. basic.py
Basic database querying with natural language using ToolFront's `ask()` method.

```bash
python basic.py
```

### 2. pdf_extraction.py
Simple PDF invoice extraction example:
- Basic invoice data extraction from PDF
- Shows type annotation usage with Pydantic models
- Good starting point for understanding ToolFront document processing

```bash
python pdf_extraction.py
```

### 3. invoice_processing_workflow.py
This is a basic invoice processing workflow that shows you how to extract structured data out of PDFs and save them to CSVs or use them as part of larger workflows.

```bash
python invoice_processing_workflow.py
```

This example shows how ToolFront PDF extraction fits into a complete business automation pipeline.

## Getting Started

1. Install ToolFront:
```bash
# For PDF processing
pip install toolfront[document-pdf]

# For Office documents (Word, PowerPoint, Excel)
pip install toolfront[document-office]

# For all document formats (includes cloud services)
pip install toolfront[document-all]
```

2. Set up your environment variables in `.env`:
```env
# Your LLM key(required)
ANTHROPIC_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key

# For database examples (optional)
POSTGRES_URL=postgresql://user:pass@host/database
SNOWFLAKE_URL=snowflake://user:pass@account/database
```

3. Run the examples:
```bash
python examples/pdf_extraction.py
```

## Key Features Demonstrated

### Document Processing
- Extract structured data from PDFs automatically
- Convert unstructured documents to JSON/Pydantic models
- Perfect for invoice processing, contract analysis, etc.

### Database Analysis  
- Natural language queries across any database
- Cross-database analytics
- Automated reporting

## Important: Type Annotations

**ToolFront uses Python type annotations to determine return types:**

```python
# Returns dict by default (new in v0.2.0)
result = doc.ask("Extract data")

# Returns validated Pydantic model
invoice: Invoice = doc.ask("Extract invoice data")

# Returns list of dictionaries  
items: list[dict] = doc.ask("Extract line items")
```

**This type annotation requirement isn't well documented yet** - it's a known UX issue we're working on.

## Tips

1. **Always use type annotations** when you want structured output
2. **Be specific in prompts**: The more detailed your request, the better the extraction
3. **Handle errors**: Wrap extraction in try/catch for production use
