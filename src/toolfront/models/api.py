import json
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import yaml
from pydantic import BaseModel, Field, computed_field, model_validator

from toolfront.config import TIMEOUT_SECONDS
from toolfront.models.base import DataSource


class HTTPMethod(str, Enum):
    """Valid HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

    @classmethod
    def get_supported_methods(cls) -> set[str]:
        """Get all supported HTTP methods."""
        return {method.value for method in cls}


class Endpoint(BaseModel):
    method: HTTPMethod = Field(
        ...,
        description="HTTP method.",
    )

    path: str = Field(
        ...,
        description="Full endpoint path in slash notation with path parameter names between curly braces e.g. '/path/to/endpoint/{{param}}'.",
    )


class Request(BaseModel):
    endpoint: Endpoint = Field(
        ...,
        description="API endpoint.",
    )

    path_params: dict[str, Any] | None = Field(
        None,
        description="Optional path parameters in JSON format e.g. {'param': 'value'}.",
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


class API(DataSource, ABC):
    """Natural language interface for OpenAPI/Swagger APIs.

    Parameters
    ----------
    spec : dict | str
        OpenAPI specification as URL, file path, or dictionary.
    headers : dict[str, str], optional
        HTTP headers for authentication.
    params : dict[str, str], optional
        Query parameters for all requests.
    """

    spec: dict | str = Field(..., description="API specification config.", exclude=True)
    endpoints: list[str] = Field(..., description="List of available endpoints.")
    headers: dict[str, str] | None = Field(None, description="Additional headers to include in requests.", exclude=True)
    params: dict[str, str] | None = Field(None, description="Query parameters to include in requests.", exclude=True)

    def __init__(
        self,
        spec: dict | str | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(spec=spec, headers=headers, params=params, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url='{self.url}')"

    @model_validator(mode="before")
    def validate_model(cls, v: Any) -> Any:
        spec = v.get("spec")

        if isinstance(spec, str):
            parsed_url = urlparse(spec)
            match parsed_url.scheme:
                case "file":
                    path = Path(parsed_url.path)
                    if not path.exists():
                        raise ConnectionError(f"OpenAPI spec file not found: {path}")
                    with path.open() as f:
                        v["spec"] = yaml.safe_load(f) if path.suffix.lower() in [".yaml", ".yml"] else json.load(f)
                case "http" | "https":
                    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
                        response = client.get(parsed_url.geturl())
                        response.raise_for_status()
                        v["spec"] = response.json()
                case _:
                    raise ValueError("Invalid API spec URL")
        elif not isinstance(spec, dict):
            raise ValueError("Invalid API spec. Must be a URL string or a dictionary.")

        # Get the endpoints from the spec
        paths = v["spec"].get("paths", {})

        if not paths:
            raise RuntimeError("No endpoints found in OpenAPI spec")

        endpoints = []
        for path, methods in paths.items():
            for method in methods:
                if method.upper() in [http_method.value.upper() for http_method in HTTPMethod]:
                    endpoints.append(f"{method.upper()} {path}")

        v["endpoints"] = endpoints

        return v

    @computed_field
    @property
    def url(self) -> str:
        """Base URL for the API."""
        if isinstance(self.spec, dict):
            return self.spec.get("servers", [{}])[0].get("url", "")
        return ""

    def tools(self) -> list[callable]:
        """Available tool methods for API operations.

        Returns
        -------
        list[callable]
            Methods for endpoint inspection and request execution.
        """
        return [self.inspect_endpoint, self.request]

    async def inspect_endpoint(self, endpoint: Endpoint) -> dict[str, Any]:
        """Inspect the structure of an API endpoint.

        TO PREVENT ERRORS, ALWAYS ENSURE THE ENDPOINT EXISTS BEFORE INSPECTING IT.

        Instructions:
        1. Use this tool to understand endpoint structure like request parameters and response schema
        2. Inspecting endpoints helps understand the structure of the data
        3. Always inspect endpoints before writing queries to understand their structure and prevent errors
        """
        inspect = self.spec.get("paths", {}).get(endpoint.path, {}).get(endpoint.method.lower(), {})
        if not inspect:
            raise RuntimeError(f"Endpoint not found: {endpoint.method} {endpoint.path}")
        return inspect

    async def request(
        self,
        request: Request,
    ) -> Any:
        """Make a request to an API endpoint.

        TO PREVENT ERRORS, ALWAYS ENSURE ENDPOINTS EXIST AND YOU ARE USING THE CORRECT METHOD, PATH, AND PARAMETERS.
        NEVER PASS API KEYS OR SECRETS TO THIS TOOL. SECRETS AND API KEYS WILL BE AUTOMATICALLY INJECTED INTO THE REQUEST.

        Instructions:
        1. Only make requests to endpoints that have been explicitly discovered, searched for, or referenced in the conversation.
        2. Before making requests, inspect the underlying endpoints to understand their config and prevent errors.
        3. When a request fails or returns unexpected results, examine the endpoint to diagnose the issue and then retry.
        """

        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.request(
                method=request.endpoint.method.upper(),
                url=f"{self.url}{request.endpoint.path.format(**(request.path_params or {}))}",
                json=request.body,
                params={**(request.params or {}), **(self.params or {})},
                headers={**(request.headers or {}), **(self.headers or {})},
            )
            response.raise_for_status()
            return response.json()
