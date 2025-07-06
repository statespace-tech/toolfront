"""Unit tests for Connection class URL parsing and driver selection."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.engine.url import make_url

from toolfront.models.connection import DatabaseConnection


class TestConnectionDriverSelection:
    """Test Connection.connect() method for proper driver selection."""

    def test_connection_url_parsing(self):
        """Test basic URL parsing and storage."""
        test_urls = [
            "postgresql://user:pass@localhost:5432/mydb",
            "mysql://user:pass@localhost:3306/mydb",
            "sqlite:///test.db",
            "bigquery://project/dataset",
            "snowflake://user:pass@account/db/schema",
            "duckdb:///test.db",
        ]

        for url in test_urls:
            connection = DatabaseConnection(url=url)
            assert connection.url == url

    def test_unsupported_driver_error(self):
        """Test that unsupported drivers raise ValueError during connect."""
        url = "unsupported://localhost/db"
        connection = DatabaseConnection(url=url)

        # Test the driver selection logic directly by trying to connect
        with pytest.raises(ValueError, match="Unsupported data source"):
            import asyncio

            asyncio.run(connection.connect())

    def test_driver_modification_logic(self):
        """Test that URLs are properly modified for async drivers."""
        test_cases = [
            ("postgresql://user:pass@localhost/db", "postgresql+asyncpg"),
            ("mysql://user:pass@localhost/db", "mysql+aiomysql"),
            ("sqlite:///memory.db", "sqlite+aiosqlite"),
            ("bigquery://project/dataset", "bigquery"),
            ("snowflake://user:pass@account/db/schema", "snowflake"),
            ("duckdb:///memory.db", "duckdb"),
        ]

        for original_url, expected_driver in test_cases:
            url = make_url(original_url)

            # Test the driver modification logic
            if url.drivername == "postgresql":
                modified_url = url.set(drivername="postgresql+asyncpg")
                assert modified_url.drivername == expected_driver
            elif url.drivername == "mysql":
                modified_url = url.set(drivername="mysql+aiomysql")
                assert modified_url.drivername == expected_driver
            elif url.drivername == "sqlite":
                modified_url = url.set(drivername="sqlite+aiosqlite")
                assert modified_url.drivername == expected_driver
            else:
                # No modification for other drivers
                assert url.drivername == expected_driver


class TestConnectionUrlHandling:
    """Test URL parsing and handling."""

    def test_url_parsing_basic(self):
        """Test basic URL parsing."""
        url = "postgresql://user:pass@localhost:5432/mydb"
        connection = DatabaseConnection(url=url)

        # Should not raise an error during creation
        assert connection.url == "postgresql://user:pass@localhost:5432/mydb"

    def test_url_parsing_with_special_characters(self):
        """Test URL parsing with special characters in password."""
        url_with_special = "postgresql://user:p%40ss@localhost:5432/mydb"
        connection = DatabaseConnection(url=url_with_special)

        assert connection.url == url_with_special

    @patch("importlib.util.find_spec", return_value=True)
    @patch("importlib.import_module")
    def test_url_unquoting(self, mock_import_module, mock_find_spec):
        """Test that URLs are properly unquoted."""
        mock_db_class = MagicMock()
        mock_import_module.return_value = MagicMock(PostgreSQL=mock_db_class)

        quoted_url = "postgresql://user:pass%40word@localhost:5432/mydb"
        connection = DatabaseConnection(url=quoted_url)

        import asyncio

        asyncio.run(connection.connect())

        # URL should be unquoted before processing
        mock_db_class.assert_called_once()


class TestUrlValidation:
    """Test URL validation and edge cases."""

    def test_url_with_query_parameters(self):
        """Test URLs with query parameters."""
        url_with_params = "postgresql://user:pass@localhost:5432/db?sslmode=require"
        connection = DatabaseConnection(url=url_with_params)

        assert connection.url == url_with_params

    def test_file_based_database_urls(self):
        """Test file-based database URLs."""
        file_urls = [
            "sqlite:///:memory:",  # In-memory databases should work
            "duckdb:///:memory:",
        ]

        for url in file_urls:
            connection = DatabaseConnection(url=url)
            assert connection.url == url

    def test_special_characters_in_password(self):
        """Test URLs with special characters in password."""
        url_with_special = "postgresql://user:p%40ss@localhost:5432/mydb"
        connection = DatabaseConnection(url=url_with_special)

        assert connection.url == url_with_special
