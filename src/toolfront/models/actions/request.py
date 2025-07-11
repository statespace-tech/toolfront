from typing import Any

from pydantic import BaseModel, Field

from toolfront.models.connections.api import APIConnection
from toolfront.types import HTTPMethod


class Request(BaseModel):
    """API endpoint."""

    connection: APIConnection = Field(..., description="API connection.")

    method: HTTPMethod = Field(
        ...,
        description="HTTP method.",
    )

    path: str = Field(
        ...,
        description="Full endpoint path with path parameters between curly braces e.g. '/users/org_123/user_123'.",
    )

    body: dict[str, Any] | None = Field(
        None,
        description="Optional request body in JSON format. Only required for POST, PUT, PATCH methods e.g. {'name': 'John', 'age': 30}.",
    )

    headers: dict[str, Any] | None = Field(
        None,
        description="Optional request headers in JSON format.",
    )

    params: dict[str, Any] | None = Field(
        None,
        description="Optional request parameters in JSON format.",
    )

    description: str = Field(
        ...,
        description="A clear business-focused description of what the request does.",
    )
