"""Unit tests for API authentication handling."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urlparse

from toolfront.main import process_datasource
from toolfront.models.api import API
from toolfront.models.connection import APIConnection


class TestAPIAuthDetection:
    """Test API authentication detection and routing."""

    @pytest.mark.asyncio
    async def test_polygon_style_query_auth(self):
        """Test that Polygon-style query parameter auth stays in query params."""
        # Mock OpenAPI spec with query-based auth
        mock_spec = {
            "servers": [{"url": "https://api.polygon.io"}],
            "components": {"securitySchemes": {"apiKey": {"type": "apiKey", "name": "apiKey", "in": "query"}}},
        }

        with patch("toolfront.main.get_openapi_spec", return_value=mock_spec):
            url_map = await process_datasource("https://api.polygon.io/openapi?apiKey=MY_KEY&other=value")

        # Check the result
        api_url = list(url_map.keys())[0]
        extra = url_map[api_url]["extra"]

        assert extra["query_params"] == {"other": "value"}
        assert extra["auth_query_params"] == {"apiKey": "MY_KEY"}
        assert extra["auth_headers"] == {}

    @pytest.mark.asyncio
    async def test_header_based_auth(self):
        """Test that header-based auth gets moved to headers."""
        # Mock OpenAPI spec with header-based auth
        mock_spec = {
            "servers": [{"url": "https://api.example.com"}],
            "components": {"securitySchemes": {"apiKey": {"type": "apiKey", "name": "apiKey", "in": "header"}}},
        }

        with patch("toolfront.main.get_openapi_spec", return_value=mock_spec):
            url_map = await process_datasource("https://api.example.com/openapi?apiKey=MY_KEY&other=value")

        api_url = list(url_map.keys())[0]
        extra = url_map[api_url]["extra"]

        assert extra["query_params"] == {"other": "value"}
        assert extra["auth_headers"] == {"apiKey": "MY_KEY"}
        assert extra["auth_query_params"] == {}

    @pytest.mark.asyncio
    async def test_bearer_token_auth(self):
        """Test bearer token authentication."""
        # Mock OpenAPI spec with bearer auth
        mock_spec = {
            "servers": [{"url": "https://api.example.com"}],
            "components": {"securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}},
        }

        with patch("toolfront.main.get_openapi_spec", return_value=mock_spec):
            url_map = await process_datasource("https://api.example.com/openapi?token=MY_TOKEN&other=value")

        api_url = list(url_map.keys())[0]
        extra = url_map[api_url]["extra"]

        assert extra["query_params"] == {"other": "value"}
        assert extra["auth_headers"] == {"Authorization": "Bearer MY_TOKEN"}
        assert extra["auth_query_params"] == {}

    @pytest.mark.asyncio
    async def test_no_spec_heuristics(self):
        """Test fallback heuristics when no OpenAPI spec is available."""
        # Mock no spec returned
        with patch("toolfront.main.get_openapi_spec", return_value={}):
            # Test bearer/token -> header
            url_map = await process_datasource("https://api.example.com/openapi?bearer=MY_BEARER")
            api_url = list(url_map.keys())[0]
            extra = url_map[api_url]["extra"]
            assert extra["auth_headers"] == {"Authorization": "Bearer MY_BEARER"}

            # Test apiKey -> query params (default)
            url_map = await process_datasource("https://api.example.com/openapi?apiKey=MY_KEY")
            api_url = list(url_map.keys())[0]
            extra = url_map[api_url]["extra"]
            assert extra["auth_query_params"] == {"apiKey": "MY_KEY"}
            assert extra["auth_headers"] == {}

    @pytest.mark.asyncio
    async def test_multiple_auth_params(self):
        """Test handling multiple auth parameters."""
        with patch("toolfront.main.get_openapi_spec", return_value={}):
            url_map = await process_datasource(
                "https://api.example.com/openapi?token=MY_TOKEN&api_key=MY_KEY&regular=value"
            )

        api_url = list(url_map.keys())[0]
        extra = url_map[api_url]["extra"]

        # Token should go to header
        assert extra["auth_headers"] == {"Authorization": "Bearer MY_TOKEN"}
        # api_key should stay in query
        assert extra["auth_query_params"] == {"api_key": "MY_KEY"}
        # Regular param should remain
        assert extra["query_params"] == {"regular": "value"}

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self):
        """Test case-insensitive parameter matching."""
        mock_spec = {
            "servers": [{"url": "https://api.example.com"}],
            "components": {
                "securitySchemes": {
                    "apiKey": {
                        "type": "apiKey",
                        "name": "apikey",  # lowercase in spec
                        "in": "header",
                    }
                }
            },
        }

        with patch("toolfront.main.get_openapi_spec", return_value=mock_spec):
            # Pass uppercase apiKey
            url_map = await process_datasource("https://api.example.com/openapi?apiKey=MY_KEY")

        api_url = list(url_map.keys())[0]
        extra = url_map[api_url]["extra"]

        # Should still match and move to headers
        assert extra["auth_headers"] == {"apikey": "MY_KEY"}

    @pytest.mark.asyncio
    async def test_server_url_handling(self):
        """Test various server URL patterns from OpenAPI spec."""
        test_cases = [
            # Absolute URL in spec
            {
                "spec_server": "https://api.example.com/v1",
                "input_url": "https://api.example.com/openapi",
                "expected": "https://api.example.com/v1",
            },
            # Relative URL in spec
            {
                "spec_server": "/api/v1",
                "input_url": "https://api.example.com/openapi",
                "expected": "https://api.example.com/api/v1",
            },
            # No server URL in spec
            {
                "spec_server": None,
                "input_url": "https://api.example.com/openapi",
                "expected": "https://api.example.com",
            },
        ]

        for case in test_cases:
            mock_spec = {"servers": []}
            if case["spec_server"]:
                mock_spec["servers"] = [{"url": case["spec_server"]}]

            with patch("toolfront.main.get_openapi_spec", return_value=mock_spec):
                url_map = await process_datasource(case["input_url"])

            api_url = list(url_map.keys())[0]
            assert api_url == case["expected"]


class TestAPIRequestAuth:
    """Test API request method with authentication."""

    @pytest.mark.asyncio
    async def test_request_merges_auth_headers(self):
        """Test that request method properly merges auth headers."""
        api = API(
            url=urlparse("https://api.example.com"),
            auth_headers={"X-API-Key": "MY_KEY"},
            query_params={"default": "value"},
            auth_query_params={"apiKey": "MY_KEY"},
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"result": "success"}
            mock_response.raise_for_status = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await api.request(
                method="GET", path="/users", headers={"User-Agent": "Test"}, params={"page": "1"}
            )

            # Check the call
            mock_client.request.assert_called_once_with(
                method="GET",
                url="https://api.example.com/users",
                json=None,
                params={"page": "1", "default": "value", "apiKey": "MY_KEY"},
                headers={"X-API-Key": "MY_KEY", "User-Agent": "Test"},
            )

            assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_request_timeout(self):
        """Test that requests have proper timeout."""
        api = API(url=urlparse("https://api.example.com"))

        with patch("httpx.AsyncClient") as mock_client_class:
            # Check that AsyncClient is created with timeout
            mock_client_class.return_value.__aenter__.return_value = AsyncMock()

            try:
                await api.request("GET", "/test")
            except:
                pass  # We don't care about the result, just the client creation

            mock_client_class.assert_called_with(timeout=30.0)


class TestAPIConnectionIntegration:
    """Test APIConnection integration with auth."""

    @pytest.mark.asyncio
    async def test_connection_creates_api_with_auth(self):
        """Test that APIConnection properly passes auth to API instance."""
        connection = APIConnection(url="https://api.example.com")

        url_map = {
            "https://api.example.com": {
                "parsed": urlparse("https://api.example.com"),
                "extra": {
                    "openapi_spec": {"info": {"title": "Test API"}},
                    "query_params": {"regular": "param"},
                    "auth_headers": {"X-API-Key": "MY_KEY"},
                    "auth_query_params": {"apiKey": "MY_KEY"},
                },
            }
        }

        api = await connection.connect(url_map)

        assert isinstance(api, API)
        assert api.auth_headers == {"X-API-Key": "MY_KEY"}
        assert api.auth_query_params == {"apiKey": "MY_KEY"}
        assert api.query_params == {"regular": "param"}
        assert api.openapi_spec == {"info": {"title": "Test API"}}
