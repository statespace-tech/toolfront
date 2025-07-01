"""Test data serialization with real database results."""

import pandas as pd
import pytest

from toolfront.models.connection import DatabaseConnection
from toolfront.models.query import Query as QueryModel
from toolfront.tools import query_database
from toolfront.utils import serialize_dataframe, serialize_response


async def execute_query(url: str, sql: str) -> str:
    """Helper function to execute queries in tests."""
    connection = DatabaseConnection(url=url)
    query_obj = QueryModel(connection=connection, code=sql, description="Test query")

    # Create a mock context since we don't need real MCP context for tests
    class MockContext:
        pass

    ctx = MockContext()
    return await query_database(ctx, query_obj)


async def execute_ddl(url: str, sql: str) -> None:
    """Helper function to execute DDL statements in tests (bypasses read-only mode)."""
    connection = DatabaseConnection(url=url)
    db = await connection.connect()
    # Use the database's execute method directly, which doesn't set read-only mode
    from sqlalchemy import create_engine, text

    # Get sync URL and execute DDL directly
    if hasattr(db, "_get_sync_url"):
        sync_url = db._get_sync_url(db.url)
        engine = create_engine(sync_url)
        with engine.connect() as conn:
            # Split multi-statement SQL for DDL
            statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
            for statement in statements:
                conn.execute(text(statement))
                conn.commit()


class TestRealDataSerialization:
    """Test serialization of real database query results."""

    @pytest.mark.asyncio
    async def test_postgresql_data_types(self, postgres_url):
        """Test serialization of PostgreSQL-specific data types."""
        # Create test table with various data types
        create_table_sql = """
        DROP TABLE IF EXISTS data_types_test;
        CREATE TABLE data_types_test (
            id SERIAL PRIMARY KEY,
            text_col TEXT,
            varchar_col VARCHAR(50),
            int_col INTEGER,
            bigint_col BIGINT,
            decimal_col DECIMAL(10,2),
            float_col FLOAT,
            bool_col BOOLEAN,
            date_col DATE,
            timestamp_col TIMESTAMP,
            json_col JSONB
        );
        """

        await execute_ddl(postgres_url, create_table_sql)

        # Insert test data
        insert_sql = """
        INSERT INTO data_types_test (
            text_col, varchar_col, int_col, bigint_col, decimal_col, 
            float_col, bool_col, date_col, timestamp_col, json_col
        ) VALUES (
            'Test text with special chars: áéíóú & <>"''',
            'Short text',
            42,
            9223372036854775807,
            123.45,
            3.14159,
            true,
            '2024-01-15',
            '2024-01-15 10:30:00',
            '{"key": "value", "number": 123, "nested": {"array": [1,2,3]}}'
        );
        """

        await execute_ddl(postgres_url, insert_sql)

        # Query and test serialization
        result = await execute_query(postgres_url, "SELECT * FROM data_types_test")

        # Should successfully serialize without errors
        assert isinstance(result, dict)
        assert "data" in result
        data = result["data"]
        assert "rows" in data
        assert len(data["rows"]) == 1

        # Convert row data to dict using column headers
        columns = data["columns"]
        row_data = data["rows"][0]
        row = dict(zip(columns, row_data, strict=False))
        assert row["text_col"] == "Test text with special chars: áéíóú & <>\"'"
        # DataFrame serialization converts to strings
        assert row["int_col"] == "42"
        # DataFrame serialization converts to strings
        assert row["bool_col"] == "True"
        assert "2024-01-15" in str(row["date_col"])

    @pytest.mark.asyncio
    async def test_mysql_data_types(self, mysql_url):
        """Test serialization of MySQL-specific data types."""
        # Create test table with various data types
        create_table_sql = """
        DROP TABLE IF EXISTS mysql_types_test;
        CREATE TABLE mysql_types_test (
            id INT AUTO_INCREMENT PRIMARY KEY,
            text_col TEXT,
            varchar_col VARCHAR(50),
            int_col INT,
            bigint_col BIGINT,
            decimal_col DECIMAL(10,2),
            float_col FLOAT,
            bool_col BOOLEAN,
            date_col DATE,
            datetime_col DATETIME,
            enum_col ENUM('small', 'medium', 'large')
        );
        """

        await execute_ddl(mysql_url, create_table_sql)

        # Insert test data
        insert_sql = """
        INSERT INTO mysql_types_test (
            text_col, varchar_col, int_col, bigint_col, decimal_col,
            float_col, bool_col, date_col, datetime_col, enum_col
        ) VALUES (
            'MySQL test with emojis: 🚀 📊 💾',
            'Short text',
            42,
            9223372036854775807,
            123.45,
            3.14159,
            1,
            '2024-01-15',
            '2024-01-15 10:30:00',
            'medium'
        );
        """

        await execute_ddl(mysql_url, insert_sql)

        # Query and test serialization
        result = await execute_query(mysql_url, "SELECT * FROM mysql_types_test")

        # Should successfully serialize without errors
        assert isinstance(result, dict)
        assert "data" in result
        data = result["data"]
        assert "rows" in data
        assert len(data["rows"]) == 1

        # Convert row data to dict using column headers
        columns = data["columns"]
        row_data = data["rows"][0]
        row = dict(zip(columns, row_data, strict=False))
        assert "🚀" in row["text_col"]
        # DataFrame serialization converts to strings
        assert row["int_col"] == "42"
        assert row["enum_col"] == "medium"

    @pytest.mark.asyncio
    async def test_large_result_set_truncation(self, postgres_url):
        """Test that large result sets are properly truncated."""
        from toolfront.config import MAX_DATA_ROWS

        # Create table with more rows than MAX_DATA_ROWS
        create_sql = """
        DROP TABLE IF EXISTS large_table_test;
        CREATE TABLE large_table_test (
            id SERIAL PRIMARY KEY,
            data TEXT
        );
        """
        await execute_ddl(postgres_url, create_sql)

        # Insert more rows than the limit
        rows_to_insert = MAX_DATA_ROWS + 10
        insert_sql = f"""
        INSERT INTO large_table_test (data)
        SELECT 'Row ' || generate_series(1, {rows_to_insert})
        """
        await execute_ddl(postgres_url, insert_sql)

        # Query all data
        result = await execute_query(postgres_url, "SELECT * FROM large_table_test ORDER BY id")

        assert isinstance(result, dict)
        data = result["data"]

        # Should be truncated to MAX_DATA_ROWS
        assert len(data["rows"]) == MAX_DATA_ROWS

    @pytest.mark.asyncio
    async def test_null_and_empty_values(self, postgres_url):
        """Test serialization of NULL and empty values."""
        create_sql = """
        DROP TABLE IF EXISTS null_test;
        CREATE TABLE null_test (
            id SERIAL PRIMARY KEY,
            nullable_text TEXT,
            empty_text TEXT,
            nullable_int INTEGER,
            zero_int INTEGER
        );
        """
        await execute_ddl(postgres_url, create_sql)

        insert_sql = """
        INSERT INTO null_test (nullable_text, empty_text, nullable_int, zero_int) VALUES
        (NULL, '', NULL, 0),
        ('actual text', '', 42, 0),
        (NULL, 'not empty', NULL, 123);
        """
        await execute_ddl(postgres_url, insert_sql)

        result = await execute_query(postgres_url, "SELECT * FROM null_test ORDER BY id")

        assert isinstance(result, dict)
        data = result["data"]
        assert len(data["rows"]) == 3

        # Check NULL handling - convert first row to dict
        columns = data["columns"]
        first_row_data = data["rows"][0]
        first_row = dict(zip(columns, first_row_data, strict=False))
        # NULL values preserved as None
        assert first_row["nullable_text"] is None
        assert first_row["empty_text"] == ""
        # NULL values preserved as None
        assert first_row["nullable_int"] is None
        assert first_row["zero_int"] == "0"

    def test_dataframe_serialization_edge_cases(self, sample_data):
        """Test DataFrame serialization with edge cases."""
        # Add edge case data to sample dataframe
        edge_case_df = sample_data.copy()

        # Add rows with edge cases
        edge_cases = pd.DataFrame(
            {
                "id": [6, 7, 8],
                "name": [None, "", "Name with\nnewlines\tand\ttabs"],
                "email": ["test@example.com", None, "unicode@tëst.com"],
                "age": [None, 0, 999],
                "active": [None, False, True],
            }
        )

        combined_df = pd.concat([edge_case_df, edge_cases], ignore_index=True)

        # Test serialization
        result = serialize_dataframe(combined_df)

        # Should not raise exceptions
        assert isinstance(result, dict)
        assert result["row_count"] == 8

        # Get the data structure
        data = result["data"]
        assert len(data["rows"]) == 8

        # Convert rows to list of dicts for easier testing
        columns = data["columns"]
        rows_as_dicts = [dict(zip(columns, row, strict=False)) for row in data["rows"]]

        # Check edge cases
        null_name_row = next(row for row in rows_as_dicts if row["id"] == "6")
        assert null_name_row["name"] is None

        empty_name_row = next(row for row in rows_as_dicts if row["id"] == "7")
        assert empty_name_row["name"] == ""

        special_chars_row = next(row for row in rows_as_dicts if row["id"] == "8")
        assert "\n" in special_chars_row["name"]
        assert "\t" in special_chars_row["name"]

    def test_serialize_response_with_metadata(self):
        """Test serialize_response with basic data."""
        test_data = [{"id": 1, "value": "test"}, {"id": 2, "value": "another"}]

        # Test basic serialize_response functionality
        result = serialize_response(test_data)

        # serialize_response returns a dict, not JSON string
        assert isinstance(result, dict)
        assert result["data"] == test_data
        assert result["type"] == "list"
