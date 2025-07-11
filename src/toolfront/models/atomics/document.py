import logging
from abc import ABC

from pydantic import BaseModel, Field, computed_field

from toolfront.models.connections.library import LibraryConnection
from toolfront.types import DocumentType

logger = logging.getLogger("toolfront")


class DocumentError(Exception):
    """Exception for document-related errors."""

    pass


class Document(BaseModel, ABC):
    """Abstract base class for documents."""

    connection: LibraryConnection = Field(..., description="Library connection.")

    document_path: str = Field(
        ...,
        description="Document path in relative to the library url e.g. 'path/to/file.pdf''",
    )

    @computed_field
    @property
    def document_type(self) -> str:
        return DocumentType.from_file_extension(self.document_path).value
