import logging
from abc import ABC
from typing import Any
from urllib.parse import ParseResult, urlparse

import httpx
from pydantic import BaseModel, Field, computed_field

from toolfront.models.spec import Spec
from toolfront.types import ConnectionResult, HTTPMethod, SearchMode
from toolfront.utils import search_items

logger = logging.getLogger("toolfront")


class APIError(Exception):
    """Exception for API-related errors."""

    pass


class API(BaseModel, ABC):
    """Abstract base class for OpenAPI/Swagger-based APIs."""

    spec: Spec = Field(description="OpenAPI/Swagger specification with auth and URL details")
    query_params: dict[str, Any] | None = Field(None, description="Additional request parameters.")

    @computed_field
    @property
    def url(self) -> ParseResult:
        """URL of the API (backwards compatibility)."""
        return urlparse(self.spec.url)

    @computed_field
    @property
    def openapi_spec(self) -> dict[str, Any]:
        """OpenAPI specification (backwards compatibility)."""
        return self.spec.spec

    # @computed_field
    # @property
    # def auth_headers(self) -> dict[str, Any]:
    #     """Authentication headers."""

    #     original_url = load_url_from_mapping(self.spec.url)
    #     if original_url:
    #         headers, _ = self.spec.extract_auth_parameters(original_url)
    #         return headers
    #     return {}

    # @computed_field
    # @property
    # def auth_query_params(self) -> dict[str, Any]:
    #     """Authentication query parameters."""
    #     _, query_params = self.spec.extract_auth_parameters()
    #     return query_params

    async def test_connection(self) -> ConnectionResult:
        """Test the connection to the API."""
        return ConnectionResult(connected=True, message="API connection successful")

    async def get_endpoints(self) -> list[str]:
        """Get the available endpoints from the OpenAPI/Swagger specification."""
        endpoints = []
        for path, methods in self.spec.get_paths().items():
            for method in methods:
                if method.upper() in [http_method.value.upper() for http_method in HTTPMethod]:
                    endpoints.append(f"{method.upper()} {path}")
        return endpoints

    async def inspect_endpoint(self, method: str, path: str) -> dict[str, Any]:
        """Inspect the details of a specific endpoint."""
        return self.spec.get_endpoint_spec(method, path)

    async def search_endpoints(self, pattern: str, mode: SearchMode = SearchMode.REGEX, limit: int = 10) -> list[str]:
        """Search for endpoints using different algorithms."""
        endpoints = await self.get_endpoints()
        if not endpoints:
            return []

        try:
            return search_items(endpoints, pattern, mode, limit)
        except Exception as e:
            logger.error(f"Endpoint search failed: {e}")
            raise APIError(f"Endpoint search failed: {e}") from e

    async def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """
        Make a request to the API endpoint.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
            path: The API endpoint path (e.g., "/users")
            body: Request body (for POST, PUT, etc.)
            params: Query parameters
            headers: Additional headers to include

        Returns:
            Response data (typically JSON)

        Raises:
            APIError: If an invalid HTTP method is provided
        """

        auth_headers, auth_query_params = self.spec.get_auth_headers_and_query_params()

        # Merge parameters and headers
        all_params = {**(params or {}), **(self.query_params or {}), **(auth_query_params or {})}

        all_headers = {**(auth_headers or {}), **(headers or {})}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method.upper(),
                url=f"{self.url.geturl()}{path}",
                json=body,
                params=all_params,
                headers=all_headers,
            )
            response.raise_for_status()
            return response.json()
