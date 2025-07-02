"""Unit tests for the discover tool with password masking."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from toolfront.main import process_datasource
from toolfront.tools import discover


class TestDiscoverPasswordMasking:
    """Test that the discover tool properly masks database passwords."""

    @pytest.mark.asyncio
    async def test_discover_masks_database_password(self):
        """Test that database URLs have passwords masked in discover output."""
        # Process a database URL with password
        url = "postgresql://user:secretpass@localhost:5432/mydb"
        url_obj, metadata = await process_datasource(url)

        # Create a mock context with the url_objects
        ctx = MagicMock()
        ctx.request_context.lifespan_context.url_objects = [url_obj]

        # Call discover
        result = await discover(ctx)

        # Check that the password is masked
        assert "datasources" in result
        assert len(result["datasources"]) == 1
        assert result["datasources"][0] == "postgresql://user:***@localhost:5432/mydb"
        assert "secretpass" not in result["datasources"][0]

    @pytest.mark.asyncio
    async def test_discover_preserves_api_urls(self):
        """Test that API URLs are not masked."""
        # Mock the OpenAPI spec download
        with patch("toolfront.main.get_openapi_spec") as mock_get_spec:
            mock_get_spec.return_value = {"servers": [{"url": "https://api.example.com/v1"}]}

            # Process an API URL
            url = "https://api.example.com/v1?apikey=secret123"
            url_obj, metadata = await process_datasource(url)

            # Create a mock context with the url_objects
            ctx = MagicMock()
            ctx.request_context.lifespan_context.url_objects = [url_obj]

            # Call discover
            result = await discover(ctx)

            # Check that API URLs are preserved as-is
            assert "datasources" in result
            assert len(result["datasources"]) == 1
            # API URLs should not be masked
            assert "https://api.example.com/v1" in result["datasources"][0]

    @pytest.mark.asyncio
    async def test_discover_handles_multiple_datasources(self):
        """Test that discover properly masks multiple database URLs."""
        # Process multiple datasources
        urls = [
            "postgresql://user1:pass1@host1:5432/db1",
            "mysql://user2:pass2@host2:3306/db2",
            "sqlite:///path/to/db.sqlite",
        ]

        # Process all URLs
        datasource_results = await asyncio.gather(*[process_datasource(url) for url in urls])

        # Extract URL objects
        url_objects = [url_obj for url_obj, metadata in datasource_results]

        # Create a mock context
        ctx = MagicMock()
        ctx.request_context.lifespan_context.url_objects = url_objects

        # Call discover
        result = await discover(ctx)

        # Check results
        assert "datasources" in result
        assert len(result["datasources"]) == 3

        # Check each datasource
        datasources = result["datasources"]

        # PostgreSQL should be masked
        pg_ds = [ds for ds in datasources if "postgresql" in ds][0]
        assert pg_ds == "postgresql://user1:***@host1:5432/db1"

        # MySQL should be masked
        mysql_ds = [ds for ds in datasources if "mysql" in ds][0]
        assert mysql_ds == "mysql://user2:***@host2:3306/db2"

        # SQLite should be unchanged (no password)
        sqlite_ds = [ds for ds in datasources if "sqlite" in ds][0]
        assert sqlite_ds == "sqlite:///path/to/db.sqlite"

    @pytest.mark.asyncio
    async def test_discover_masks_special_chars_in_password(self):
        """Test that passwords with special characters are properly masked."""
        # URL with special characters in password
        url = "postgresql://user:p@ss$w0rd!@localhost:5432/mydb"
        url_obj, metadata = await process_datasource(url)

        # Create a mock context
        ctx = MagicMock()
        ctx.request_context.lifespan_context.url_objects = [url_obj]

        # Call discover
        result = await discover(ctx)

        # Check that the password is masked
        assert "datasources" in result
        assert result["datasources"][0] == "postgresql://user:***@localhost:5432/mydb"
        assert "p@ss$w0rd!" not in result["datasources"][0]

    @pytest.mark.asyncio
    async def test_discover_handles_empty_password(self):
        """Test that empty passwords are still masked."""
        # URL with empty password
        url = "postgresql://user:@localhost:5432/mydb"
        url_obj, metadata = await process_datasource(url)

        # Create a mock context
        ctx = MagicMock()
        ctx.request_context.lifespan_context.url_objects = [url_obj]

        # Call discover
        result = await discover(ctx)

        # Check that empty password is handled (no masking needed for empty password)
        assert "datasources" in result
        assert result["datasources"][0] == "postgresql://user@localhost:5432/mydb"
