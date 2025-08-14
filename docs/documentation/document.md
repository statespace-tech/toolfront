# Document Processing

ToolFront supports data retrieval from various document formats with unified processing patterns.

---

## Connecting a Document

ToolFront all major text-based documents.

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-file-pdf:{ .middle } &nbsp; PDF"

    ```python linenums="1"
    from toolfront import Document

    # Research paper or report
    doc = Document("research_paper.pdf")
    authors = doc.ask("Who are the authors?")
    ```

=== ":fontawesome-solid-file-word:{ .middle } &nbsp; Word"

    ```python linenums="1"
    from toolfront import Document

    # Contract or document
    doc = Document("contract.docx")
    terms = doc.ask("What are the key terms?")
    ```

=== ":fontawesome-solid-file-powerpoint:{ .middle } &nbsp; PPT"

    ```python linenums="1"
    from toolfront import Document

    # Business presentation
    doc = Document("presentation.pptx")
    summary = doc.ask("Summarize the key points")
    ```

=== ":fontawesome-solid-file-code:{ .middle } &nbsp; JSON"

    ```python linenums="1"
    from toolfront import Document

    # Configuration or data file
    doc = Document("config.json")
    settings = doc.ask("What are the main settings?")
    ```

=== ":fontawesome-brands-markdown:{ .middle } &nbsp; MD"

    ```python linenums="1"
    from toolfront import Document

    # Markdown documentation
    doc = Document("README.md")
    instructions = doc.ask("How do I install this?")
    ```

=== ":fontawesome-solid-file-alt:{ .middle } &nbsp; Text"

    ```python linenums="1"
    from toolfront import Document

    # Plain text file
    doc = Document("notes.txt")
    key_points = doc.ask("Extract the key points")
    ```

=== ":fontawesome-brands-html5:{ .middle } &nbsp; HTML"

    ```python linenums="1"
    from toolfront import Document

    # Web page or report
    doc = Document("report.html")
    metrics = doc.ask("Extract performance metrics")
    ```

</div>

---

## Text Input

Process text content without files for quick analysis:

```python linenums="1"
from toolfront import Document

# Direct text processing
text_content = """
Company quarterly report shows 15% growth in revenue.
Sales increased across all regions with Europe leading at 22%.
"""
doc = Document(text=text_content)
metrics = doc.ask("Extract the key metrics")
```