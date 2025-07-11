from pydantic import BaseModel, Field

from toolfront.models.connections.library import LibraryConnection


class Read(BaseModel):
    """Storage document."""

    connection: LibraryConnection = Field(..., description="Library connection.")
