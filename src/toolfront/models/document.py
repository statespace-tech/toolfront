from pathlib import Path
from typing import Any

from markitdown import MarkItDown
from pydantic import BaseModel, Field, model_validator

from toolfront.config import CHUNK_SIZE, MARKITDOWN_TYPES, TEXT_TYPES
from toolfront.models.base import DataSource


class Pagination(BaseModel):
    value: int | float = Field(..., description="Section navigation: 0.0-0.99 for percentile, >=1 for section number.")


class Document(DataSource):
    """Natural language interface for documents.

    Supports PDF, DOCX, PPTX, XLSX, HTML, JSON, MD, TXT, XML, YAML, RTF formats.
    Documents are automatically chunked for efficient processing.

    Parameters
    ----------
    source : str, optional
        Path to document file. Mutually exclusive with text.
    text : str, optional
        Document content as text. Mutually exclusive with source.
    """

    source: str | None = Field(
        default=None,
        description="Path to a local document file. If None, the document content must provided directly via text parameter. Mutually exclusive with text.",
    )
    text: str = Field(
        description="Document content as text. If None, the document source path must be provided directly via the source parameter. Mutually exclusive with source.",
        exclude=True,
    )

    def __init__(self, source: str | None = None, text: str | None = None, **kwargs: Any) -> None:
        super().__init__(source=source, text=text, **kwargs)

    @model_validator(mode="before")
    def validate_model(cls, v: Any) -> Any:
        source_value = v.get("source")
        text_value = v.get("text")

        # Validate mutual exclusivity
        if source_value is not None and text_value is not None:
            raise ValueError("source and text cannot be provided together.")

        if source_value is None and text_value is None:
            raise ValueError("Either source or text must be provided.")

        # If text is provided, we're done
        if source_value is None:
            return v

        # Process source
        source_path = Path(source_value)
        if not source_path.exists():
            raise ValueError(f"Document path does not exist: {source_path}")

        # Extract file extension (without the dot)
        document_type = source_path.suffix[1:].lower() if source_path.suffix else ""

        # Read document based on type
        document_content = cls._read_document_content(source_path, document_type)
        v["text"] = document_content

        return v

    @classmethod
    def _read_document_content(cls, source_path: Path, document_type: str) -> str:
        """Read document content based on file type."""
        if document_type in MARKITDOWN_TYPES:
            md = MarkItDown()
            result = md.convert(source_path)
            return result.markdown
        elif document_type in TEXT_TYPES:
            return source_path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported document type: {document_type}")

    def tools(self) -> list[callable]:
        """Available tool methods for document operations.

        Returns
        -------
        list[callable]
            Methods for document reading with intelligent chunking.
        """
        return [self.read]

    async def read(
        self,
        pagination: Pagination,
    ) -> str:
        """Read the contents of a library's document with automatic chunking.

        All documents are automatically chunked into sections of 10,000 characters each for easier navigation.

        Instructions:
        1. Documents are split into 10k character chunks for all file types (PDF, DOCX, PPTX, Excel, JSON, MD, TXT, XML, YAML, RTF, HTML).
        2. Use pagination value parameter to navigate through document sections:
           - 0.0 <= pagination value < 1.0: Return section at that percentile (e.g., 0.5 = middle section)
           - pagination value >= 1: Return specific section number (e.g., 1 = first section, 2 = second section)
        3. When searching for specific information in large documents, use a "soft" binary search approach:
           - Start with an educated percentile guess based on document type and target content (e.g., 0.8 for conclusions in academic papers, 0.3 for methodology)
           - Use the context from your initial read to refine your search. If you find related but not target content, adjust percentile accordingly
           - Iterate between percentile and section number paginations to pinpoint information as you narrow down the location
        4. Use educated guesses for initial positions based on document structure (e.g., table of contents near start, conclusions near end, etc.).
        5. NEVER continue reading through the rest of the document unnecessarily once you have found the answer.
        """
        # Use the text content for chunking
        document_content = self.text

        # Calculate chunking parameters
        total_sections = (len(document_content) + CHUNK_SIZE - 1) // CHUNK_SIZE

        if total_sections == 0:
            return document_content

        # Determine section index and label based on pagination type
        if pagination.value < 1:
            # Percentile-based: convert to section index
            section_index = min(int(pagination.value * total_sections), total_sections - 1)
        else:
            section_index = min(int(pagination.value), total_sections) - 1

        start_idx = section_index * CHUNK_SIZE
        end_idx = min(start_idx + CHUNK_SIZE, len(document_content))
        return f"Section {section_index + 1} of {total_sections}:\n\n{document_content[start_idx:end_idx]}"
