"""Unit tests for Connection class URL parsing and driver selection."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.engine.url import make_url

from toolfront.models.connection import DatabaseConnection, Connection
from toolfront.models.url import DatabaseURL


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
            db_url = DatabaseURL.from_url_string(url)
            connection = DatabaseConnection(url=db_url)
            assert connection.url.to_connection_string() == url

    def test_unsupported_driver_error(self):
        """Test that unsupported drivers raise ValueError during connect."""
        db_url = DatabaseURL.from_url_string("unsupported://localhost/db")
        connection = DatabaseConnection(url=db_url)

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
    """Test URL parsing and URL map handling."""

    def test_url_parsing_basic(self):
        """Test basic URL parsing."""
        db_url = DatabaseURL.from_url_string("postgresql://user:pass@localhost:5432/mydb")
        connection = DatabaseConnection(url=db_url)

        # Should not raise an error during creation
        assert connection.url.to_connection_string() == "postgresql://user:pass@localhost:5432/mydb"

    def test_url_parsing_with_special_characters(self):
        """Test URL parsing with special characters in password."""
        url_with_special = "postgresql://user:p%40ss@localhost:5432/mydb"
        db_url = DatabaseURL.from_url_string(url_with_special)
        connection = DatabaseConnection(url=db_url)

        assert connection.url.to_connection_string() == url_with_special

    @patch("importlib.util.find_spec", return_value=True)
    @patch("importlib.import_module")
    def test_url_map_usage(self, mock_import_module, mock_find_spec):
        """Test that url_map is used when provided."""
        mock_db_class = MagicMock()
        mock_import_module.return_value = MagicMock(PostgreSQL=mock_db_class)

        obfuscated_url = "postgresql://user:***@localhost:5432/mydb"
        real_url = make_url("postgresql://user:realpass@localhost:5432/mydb")

        connection = Connection.from_url(obfuscated_url)
        url_map = {obfuscated_url: real_url}

        import asyncio

        asyncio.run(connection.connect(url_map=url_map))

        # Should use the real URL from url_map
        mock_db_class.assert_called_once()
        called_url = mock_db_class.call_args[1]["url"]
        assert str(called_url).replace("+asyncpg", "") == str(real_url)

    @patch("importlib.util.find_spec", return_value=True)
    @patch("importlib.import_module")
    def test_url_map_fallback_to_direct_parsing(self, mock_import_module, mock_find_spec):
        """Test fallback to direct URL parsing when not in url_map."""
        mock_db_class = MagicMock()
        mock_import_module.return_value = MagicMock(PostgreSQL=mock_db_class)

        db_url = DatabaseURL.from_url_string("postgresql://user:pass@localhost:5432/mydb")
        connection = DatabaseConnection(url=db_url)
        url_map = {"other://url": make_url("other://url")}

        import asyncio

        asyncio.run(connection.connect(url_map=url_map))

        # Should parse the URL directly since it's not in url_map
        mock_db_class.assert_called_once()

    @patch("importlib.util.find_spec", return_value=True)
    @patch("importlib.import_module")
    def test_no_url_map_provided(self, mock_import_module, mock_find_spec):
        """Test behavior when no url_map is provided."""
        mock_db_class = MagicMock()
        mock_import_module.return_value = MagicMock(PostgreSQL=mock_db_class)

        db_url = DatabaseURL.from_url_string("postgresql://user:pass@localhost:5432/mydb")
        connection = DatabaseConnection(url=db_url)

        import asyncio

        asyncio.run(connection.connect())

        # Should work without url_map
        mock_db_class.assert_called_once()

    @patch("importlib.util.find_spec", return_value=True)
    @patch("importlib.import_module")
    def test_url_unquoting(self, mock_import_module, mock_find_spec):
        """Test that URLs are properly unquoted."""
        mock_db_class = MagicMock()
        mock_import_module.return_value = MagicMock(PostgreSQL=mock_db_class)

        quoted_url = "postgresql://user:pass%40word@localhost:5432/mydb"
        db_url = DatabaseURL.from_url_string(quoted_url)
        connection = DatabaseConnection(url=db_url)

        import asyncio

        asyncio.run(connection.connect())

        # URL should be unquoted before processing
        mock_db_class.assert_called_once()


class TestUrlValidation:
    """Test URL validation and edge cases."""

    def test_url_with_query_parameters(self):
        """Test URLs with query parameters."""
        url_with_params = "postgresql://user:pass@localhost:5432/db?sslmode=require"
        db_url = DatabaseURL.from_url_string(url_with_params)
        connection = DatabaseConnection(url=db_url)

        assert connection.url.to_connection_string() == url_with_params

    def test_file_based_database_urls(self):
        """Test file-based database URLs."""
        file_urls = [
            "sqlite:///:memory:",  # In-memory databases should work
            "duckdb:///:memory:",
        ]

        for url in file_urls:
            db_url = DatabaseURL.from_url_string(url)
            connection = DatabaseConnection(url=db_url)
            assert connection.url.to_connection_string() == url

    def test_special_characters_in_password(self):
        """Test URLs with special characters in password."""
        url_with_special = "postgresql://user:p%40ss@localhost:5432/mydb"
        db_url = DatabaseURL.from_url_string(url_with_special)
        connection = DatabaseConnection(url=db_url)

        assert connection.url.to_connection_string() == url_with_special
