import logging
from typing import Any

from pydantic import Field

from toolfront.config import (
    NUM_DOCUMENT_SEARCH_ITEMS,
)
from toolfront.models.atomics.document import Document
from toolfront.models.connections.library import LibraryConnection
from toolfront.types import SearchMode
from toolfront.utils import serialize_response

logger = logging.getLogger("toolfront")


__all__ = [
    "search_documents",
    "read_document",
]


async def search_documents(
    connection: LibraryConnection = Field(..., description="Library connection to search."),
    pattern: str = Field(..., description="Pattern to search for."),
    mode: SearchMode = Field(default=SearchMode.REGEX, description="Search mode to use."),
) -> dict[str, Any]:
    """
    Find and return documents names that match the given pattern.

    NEVER CALL THIS TOOL MORE THAN NECESSARY. DO NOT ADJUST THE LIMIT PARAMETER UNLESS REQUIRED.

    Library Search Instructions:
    1. This tool searches for document names in a library, not their contents.
    2. Determine the best search mode to use:
        - regex:
            * Returns documents matching a regular expression pattern
            * Pattern must be a valid regex expression
            * Use when you need precise document name matching
        - bm25:
            * Returns documents using case-insensitive BM25 (Best Match 25) ranking algorithm
            * Pattern must be a sentence, phrase, or space-separated words
            * Use when searching document names with descriptive keywords
        - jaro_winkler:
            * Returns documents using case-insensitive Jaro-Winkler similarity algorithm
            * Pattern must be an existing document name.
            * Use to search for similar document names.
    3. Begin with approximate search modes like BM25 and Jaro-Winkler, and only use regex to precisely search for a specific document name.
    """
    try:
        logger.debug(f"Searching documents: {connection.url} {pattern} {mode}")
        library = await connection.connect()
        result = await library.search_documents(pattern=pattern, mode=mode, limit=NUM_DOCUMENT_SEARCH_ITEMS)
        return {"documents": result}
    except Exception as e:
        logger.error(f"Failed to search documents: {e}", exc_info=True)
        raise ConnectionError(f"Failed to search documents in {connection.url} - {str(e)}")


async def read_document(
    document: Document = Field(..., description="Document to read."),
    pagination: float = Field(description="Page/section number (1-indexed int) or percentile (0.0-1.0 float) to read."),
) -> dict[str, Any]:
    """
    Read the contents of a library's document.

    Library Read Instructions:
    1. For non-paginated documents (JSON, MD, TXT, XML, YAML, RTF), this tool reads the entire document contents.
    2. For paginated documents (PDF, DOCX, PPTX, Excel), this tool reads only specific pages/sections. Use pagination parameter strategically to target relevant content.
    3. Use pagination parameter as between 0.0 (inclusive) and 1.0 (exclusive) for percentile-based navigation or int (1+) for specific page numbers.
    4. When searching for specific information in large paginated documents, use a "soft" binary search approach:
       - Start with an educated percentile guess based on document type and target content (e.g., 0.8 for conclusions in academic papers, 0.3 for methodology)
       - Use the context from your initial read to refine your search. If you find related but not target content, adjust percentile accordingly
       - Iterate between percentile and page number paginations to pinpoint information as you narrow down the location
       - If initial pages show the document is irrelevant, abandon it quickly rather than exhaustively searching it.
    5. Use educated guesses for initial page positions based on document structure (e.g., table of contents near start, conclusions near end, etc.).
    6. Avoid over-paginating: don't read every page sequentially unless absolutely necessary for comprehensive understanding.
    """
    try:
        logger.debug(f"Reading document: {document.connection.url} {document.document_path}")
        library = await document.connection.connect()
        return serialize_response(
            await library.read_document(
                document_path=document.document_path,
                document_type=document.document_type,
                pagination=pagination,
            )
        )
    except Exception as e:
        logger.error(f"Failed to read library: {e}", exc_info=True)
        raise ConnectionError(f"Failed to read library in {document.connection.url} - {str(e)}")
