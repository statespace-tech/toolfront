from urllib.parse import unquote

from pydantic import BaseModel, Field
from sqlalchemy.engine.url import make_url

from toolfront.models.connections.database import DatabaseConnection


class Query(BaseModel):
    """Query model for both database queries and file queries."""

    connection: DatabaseConnection = Field(..., description="Database connection.")

    code: str = Field(..., description="SQL query string to execute. Must match the SQL dialect of the database.")

    description: str = Field(
        ...,
        description="A clear business-focused description of what the query does including tables and transformations used.",
    )

    @property
    def dialect(self) -> str:
        return make_url(unquote(self.connection.url)).drivername
