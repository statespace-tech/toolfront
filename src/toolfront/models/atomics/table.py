from pydantic import BaseModel, Field

from toolfront.models.connections.database import DatabaseConnection


class Table(BaseModel):
    """Unified table identifier for both database tables and file tables."""

    connection: DatabaseConnection = Field(..., description="Database connection.")

    path: str = Field(
        ...,
        description="Full table path in dot notation e.g. 'schema.table' or 'database.schema.table'.",
    )
