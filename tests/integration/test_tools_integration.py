"""Test ToolFront database integration with real database connections."""

import pytest

from toolfront.models.connection import DatabaseConnection
from toolfront.models.url import DatabaseURL
from toolfront.models.database import SearchMode


class TestDatabaseIntegration:
    """Test database integration with real database connections."""

    @pytest.mark.asyncio
    async def test_connection_testing_all_databases(self, postgres_url, mysql_url, sqlite_url, duckdb_url):
        """Test connection testing with all database types."""
        urls = [postgres_url, mysql_url, sqlite_url, duckdb_url]

        for url in urls:
            db_url = DatabaseURL.from_url_string(url)
            connection = DatabaseConnection(url=db_url)
            db = await connection.connect()
            result = await db.test_connection()

            # Should return ConnectionResult with success
            assert result.connected is True
            assert "successful" in result.message.lower() or "success" in result.message.lower()

    @pytest.mark.asyncio
    async def test_table_inspection_with_existing_tables(self, postgres_url):
        """Test table inspection with PostgreSQL system tables."""
        # Use a known system table that should always exist
        table_name = "information_schema.tables"

        db_url = DatabaseURL.from_url_string(postgres_url)
        connection = DatabaseConnection(url=db_url)
        db = await connection.connect()
        result = await db.inspect_table(table_name)

        # Should return table structure information
        assert result is not None
        # The exact structure depends on the database adapter implementation

    @pytest.mark.asyncio
    async def test_table_sampling_with_existing_data(self, postgres_url):
        """Test table sampling with PostgreSQL system tables."""
        # Use a known system table
        table_name = "information_schema.tables"

        db_url = DatabaseURL.from_url_string(postgres_url)
        connection = DatabaseConnection(url=db_url)
        db = await connection.connect()
        result = await db.sample_table(table_name, n=3)

        # Should return sample data
        assert result is not None
        # The exact structure depends on the database adapter implementation

    @pytest.mark.asyncio
    async def test_query_execution_basic_queries(self, postgres_url, mysql_url):
        """Test query execution with basic SQL queries."""
        import pandas as pd

        test_cases = [
            (postgres_url, "SELECT 1 as test_value, 'postgresql' as db_type"),
            (mysql_url, "SELECT 1 as test_value, 'mysql' as db_type"),
        ]

        for url, sql in test_cases:
            db_url = DatabaseURL.from_url_string(url)
            connection = DatabaseConnection(url=db_url)
            db = await connection.connect()
            result = await db.query(sql)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert result.iloc[0]["test_value"] == 1

    @pytest.mark.asyncio
    async def test_table_searchning_pattern_matching(self, postgres_url):
        """Test table searchning for pattern matching."""
        # Test with a common pattern
        db_url = DatabaseURL.from_url_string(postgres_url)
        connection = DatabaseConnection(url=db_url)
        db = await connection.connect()
        result = await db.search_tables("information", mode=SearchMode.REGEX, limit=10)

        assert isinstance(result, list)
        # Should return matching tables or empty results (both are valid)

    @pytest.mark.asyncio
    async def test_error_handling_invalid_queries(self, postgres_url):
        """Test that database handles invalid queries gracefully."""
        db_url = DatabaseURL.from_url_string(postgres_url)
        connection = DatabaseConnection(url=db_url)
        db = await connection.connect()

        # Test with invalid SQL - this should raise a DatabaseError
        from toolfront.models.database import DatabaseError

        with pytest.raises(DatabaseError, match="Query execution failed"):
            await db.query("SELECT FROM INVALID_SYNTAX")

    @pytest.mark.asyncio
    async def test_error_handling_nonexistent_tables(self, postgres_url):
        """Test that database handles nonexistent tables gracefully."""
        db_url = DatabaseURL.from_url_string(postgres_url)
        connection = DatabaseConnection(url=db_url)
        db = await connection.connect()

        # Test with nonexistent table - this should raise an exception
        # Using a more specific exception type
        from toolfront.models.database import DatabaseError

        with pytest.raises((DatabaseError, RuntimeError, ValueError)):
            await db.inspect_table("nonexistent_table_12345")


class TestConcurrentConnections:
    """Test concurrent database operations and connection pooling."""

    @pytest.mark.asyncio
    async def test_concurrent_queries(self, postgres_url):
        """Test multiple concurrent queries to the same database."""
        import asyncio

        import pandas as pd

        async def run_query(query_id: int):
            db_url = DatabaseURL.from_url_string(postgres_url)
            connection = DatabaseConnection(url=db_url)
            db = await connection.connect()
            result = await db.query(f"SELECT {query_id} as query_id, pg_backend_pid() as backend_pid")
            return result

        # Run 5 concurrent queries
        tasks = [run_query(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Query {i} failed: {result}"
            assert isinstance(result, pd.DataFrame)
            assert result.iloc[0]["query_id"] == i

    @pytest.mark.asyncio
    async def test_concurrent_different_databases(self, postgres_url, mysql_url):
        """Test concurrent operations on different database types."""
        import asyncio

        import pandas as pd

        async def test_postgres():
            db_url = DatabaseURL.from_url_string(postgres_url)
            connection = DatabaseConnection(url=db_url)
            db = await connection.connect()
            return await db.query("SELECT 'postgres' as db_type")

        async def test_mysql():
            db_url = DatabaseURL.from_url_string(mysql_url)
            connection = DatabaseConnection(url=db_url)
            db = await connection.connect()
            return await db.query("SELECT 'mysql' as db_type")

        # Run concurrent operations on different databases
        pg_result, mysql_result = await asyncio.gather(test_postgres(), test_mysql())

        # Both should be DataFrames with correct results
        assert isinstance(pg_result, pd.DataFrame)
        assert isinstance(mysql_result, pd.DataFrame)
        assert pg_result.iloc[0]["db_type"] == "postgres"
        assert mysql_result.iloc[0]["db_type"] == "mysql"
