"""Test database connectivity and basic operations across different database types."""

import pytest

from toolfront.models.connection import DatabaseConnection
from toolfront.models.url import DatabaseURL


class TestDatabaseConnectivity:
    """Test basic database connectivity for supported database types."""

    @pytest.mark.asyncio
    async def test_postgresql_connection(self, postgres_url):
        """Test PostgreSQL connection and basic operations."""
        db_url = DatabaseURL.from_url_string(postgres_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test connection
        result = await database.test_connection()
        assert result.connected, f"Failed to connect to PostgreSQL: {result.message}"

        # Test basic query
        query_result = await database.query("SELECT 1 as test_value")
        assert len(query_result) == 1
        assert query_result.iloc[0]["test_value"] == 1

    @pytest.mark.asyncio
    async def test_mysql_connection(self, mysql_url):
        """Test MySQL connection and basic operations."""
        db_url = DatabaseURL.from_url_string(mysql_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test connection
        result = await database.test_connection()
        assert result.connected, f"Failed to connect to MySQL: {result.message}"

        # Test basic query
        query_result = await database.query("SELECT 1 as test_value")
        assert len(query_result) == 1
        assert query_result.iloc[0]["test_value"] == 1

    @pytest.mark.asyncio
    async def test_sqlite_connection(self, sqlite_url):
        """Test SQLite connection and basic operations."""
        db_url = DatabaseURL.from_url_string(sqlite_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test connection
        result = await database.test_connection()
        assert result.connected, f"Failed to connect to SQLite: {result.message}"

        # Test basic query
        query_result = await database.query("SELECT 1 as test_value")
        assert len(query_result) == 1
        assert query_result.iloc[0]["test_value"] == 1

    @pytest.mark.asyncio
    async def test_duckdb_connection(self, duckdb_url):
        """Test DuckDB connection and basic operations."""
        db_url = DatabaseURL.from_url_string(duckdb_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test connection
        result = await database.test_connection()
        assert result.connected, f"Failed to connect to DuckDB: {result.message}"

        # Test basic query
        query_result = await database.query("SELECT 1 as test_value")
        assert len(query_result) == 1
        assert query_result.iloc[0]["test_value"] == 1

    @pytest.mark.asyncio
    async def test_sqlserver_connection(self, sqlserver_url):
        """Test SQL Server connection and basic operations."""
        db_url = DatabaseURL.from_url_string(sqlserver_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test connection
        result = await database.test_connection()
        assert result.connected, f"Failed to connect to SQL Server: {result.message}"

        # Test basic query
        query_result = await database.query("SELECT 1 as test_value")
        assert len(query_result) == 1
        assert query_result.iloc[0]["test_value"] == 1

        # Test SQL Server-specific TOP syntax
        query_result = await database.query("SELECT TOP 1 'sqlserver_test' as mode")
        assert len(query_result) == 1
        assert query_result.iloc[0]["mode"] == "sqlserver_test"

    @pytest.mark.asyncio
    async def test_connection_retry_logic(self, postgres_url):
        """Test that connection retry logic works correctly."""
        # Test with invalid URL first
        invalid_url = postgres_url.replace("5432", "9999")  # Wrong port
        db_url = DatabaseURL.from_url_string(invalid_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Should fail gracefully
        result = await database.test_connection()
        assert not result.connected, "Should not connect with invalid URL"

        # Test with valid URL should work
        db_url = DatabaseURL.from_url_string(postgres_url)
        valid_connection = DatabaseConnection(url=db_url)
        valid_database = await valid_connection.connect()
        valid_result = await valid_database.test_connection()
        assert valid_result.connected, "Should connect with valid URL"


class TestConnectionFallback:
    """Test async/sync fallback behavior across database types."""

    @pytest.mark.asyncio
    async def test_async_execution_postgresql(self, postgres_url):
        """Test async query execution with PostgreSQL."""
        db_url = DatabaseURL.from_url_string(postgres_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test async execution
        result = await database.query("SELECT 'async_test' as mode, 1 as value")
        assert len(result) == 1
        assert result.iloc[0]["mode"] == "async_test"
        assert result.iloc[0]["value"] == 1

    @pytest.mark.asyncio
    async def test_async_execution_mysql(self, mysql_url):
        """Test async query execution with MySQL."""
        db_url = DatabaseURL.from_url_string(mysql_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test async execution
        result = await database.query("SELECT 'async_test' as mode, 1 as value")
        assert len(result) == 1
        assert result.iloc[0]["mode"] == "async_test"
        assert result.iloc[0]["value"] == 1

    @pytest.mark.asyncio
    async def test_async_execution_sqlserver(self, sqlserver_url):
        """Test async query execution with SQL Server."""
        db_url = DatabaseURL.from_url_string(sqlserver_url)
        connection = DatabaseConnection(url=db_url)
        database = await connection.connect()

        # Test async execution with SQL Server syntax
        result = await database.query("SELECT 'async_test' as mode, 1 as value")
        assert len(result) == 1
        assert result.iloc[0]["mode"] == "async_test"
        assert result.iloc[0]["value"] == 1

    @pytest.mark.asyncio
    async def test_sync_fallback_in_memory_databases(self, sqlite_url, duckdb_url):
        """Test that in-memory databases work with sync fallback."""
        for url in [sqlite_url, duckdb_url]:
            db_url = DatabaseURL.from_url_string(url)
            connection = DatabaseConnection(url=db_url)
            database = await connection.connect()

            # These should work even if async fails
            result = await database.query("SELECT 'fallback_test' as mode, 1 as value")
            assert len(result) == 1
            assert result.iloc[0]["mode"] == "fallback_test"
            assert result.iloc[0]["value"] == 1
