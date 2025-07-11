from pydantic import BaseModel, Field

from toolfront.models.connections.api import APIConnection
from toolfront.types import HTTPMethod


class Endpoint(BaseModel):
    """API endpoint."""

    connection: APIConnection = Field(..., description="API connection.")

    method: HTTPMethod = Field(
        ...,
        description="HTTP method.",
    )

    path: str = Field(
        ...,
        description="Full endpoint path in slash notation with path parameter names between curly braces e.g. '/path/to/endpoint/{{param}}'.",
    )
