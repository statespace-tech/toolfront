"""Test SQL Server-specific features and functionality."""

import contextlib

import pytest

from toolfront.models.connection import Connection


class TestSQLServerFeatures:
    """Test SQL Server-specific implementation details."""

    @pytest.mark.asyncio
    async def test_sqlserver_session_initialization(self, sqlserver_url):
        """Test that SQL Server sets READ UNCOMMITTED isolation level."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        init_sql = database.initialize_session()
        assert init_sql == "SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"

        result = await database.test_connection()
        assert result.connected, f"Failed to connect to SQL Server: {result.message}"

    @pytest.mark.asyncio
    async def test_sqlserver_get_tables(self, sqlserver_url):
        """Test SQL Server table discovery."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        tables = await database.get_tables()
        assert isinstance(tables, list)

        system_tables = [
            t for t in tables if t.startswith(("information_schema.", "sys.", "INFORMATION_SCHEMA.", "SYS."))
        ]
        assert len(system_tables) == 0, f"System tables should be excluded: {system_tables}"

    @pytest.mark.asyncio
    async def test_sqlserver_schema_table_format(self, sqlserver_url):
        """Test SQL Server schema.table naming convention."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        # Create a temporary table for testing
        await database.query("""
            CREATE TABLE dbo.test_table (
                id INT PRIMARY KEY,
                name NVARCHAR(50),
                created_at DATETIME2 DEFAULT GETDATE()
            )
        """)

        try:
            # Test table discovery includes schema prefix
            tables = await database.get_tables()
            test_tables = [t for t in tables if "test_table" in t]
            assert len(test_tables) > 0, "Test table should be discovered"

            # Table should include schema prefix
            table_name = test_tables[0]
            assert "." in table_name, f"Table name should include schema: {table_name}"
            assert table_name.startswith("dbo."), f"Table should start with dbo schema: {table_name}"

            # Test inspect table with schema.table format
            schema = await database.inspect_table(table_name)
            assert len(schema) > 0, "Table schema should be returned"

            # Verify expected columns
            column_names = schema["column_name"].tolist()
            assert "id" in column_names
            assert "name" in column_names
            assert "created_at" in column_names

            # Test sample table with SQL Server TOP syntax
            sample = await database.sample_table(table_name, n=1)
            assert len(sample) == 0, "Should return empty result for empty table"

        finally:
            # Clean up
            with contextlib.suppress(Exception):
                await database.query("DROP TABLE dbo.test_table")

    @pytest.mark.asyncio
    async def test_sqlserver_data_types(self, sqlserver_url):
        """Test SQL Server data type handling."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        # Create table with various SQL Server data types
        await database.query("""
            CREATE TABLE dbo.datatype_test (
                id INT,
                text_col NVARCHAR(100),
                decimal_col DECIMAL(10,2),
                date_col DATE,
                datetime_col DATETIME2,
                bit_col BIT,
                guid_col UNIQUEIDENTIFIER DEFAULT NEWID()
            )
        """)

        try:
            # Inspect the table to verify data types
            schema = await database.inspect_table("dbo.datatype_test")
            assert len(schema) > 0

            # Verify data type mapping
            data_types = dict(zip(schema["column_name"], schema["data_type"], strict=False))
            assert "int" in data_types["id"].lower()
            assert "nvarchar" in data_types["text_col"].lower()
            assert "decimal" in data_types["decimal_col"].lower()
            assert "date" in data_types["date_col"].lower()
            assert "datetime" in data_types["datetime_col"].lower()
            assert "bit" in data_types["bit_col"].lower()

        finally:
            # Clean up
            with contextlib.suppress(Exception):
                await database.query("DROP TABLE dbo.datatype_test")

    @pytest.mark.asyncio
    async def test_sqlserver_top_syntax(self, sqlserver_url):
        """Test SQL Server TOP syntax in queries."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        # Create and populate test table
        await database.query("""
            CREATE TABLE dbo.top_test (
                id INT,
                value NVARCHAR(50)
            )
        """)

        await database.query("""
            INSERT INTO dbo.top_test (id, value) VALUES 
            (1, 'first'), (2, 'second'), (3, 'third'), (4, 'fourth'), (5, 'fifth')
        """)

        try:
            # Test TOP syntax with sample_table
            sample = await database.sample_table("dbo.top_test", n=3)
            assert len(sample) == 3, f"Should return 3 rows, got {len(sample)}"

            # Test TOP syntax in direct query
            result = await database.query("SELECT TOP 2 * FROM dbo.top_test ORDER BY id")
            assert len(result) == 2, f"Should return 2 rows, got {len(result)}"
            assert result.iloc[0]["id"] == 1
            assert result.iloc[1]["id"] == 2

        finally:
            # Clean up
            with contextlib.suppress(Exception):
                await database.query("DROP TABLE dbo.top_test")

    @pytest.mark.asyncio
    async def test_sqlserver_multiple_schemas(self, sqlserver_url):
        """Test SQL Server with multiple schemas."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        # Create a custom schema and table
        await database.query("CREATE SCHEMA test_schema")
        await database.query("""
            CREATE TABLE test_schema.multi_schema_table (
                id INT PRIMARY KEY,
                name NVARCHAR(50)
            )
        """)

        try:
            # Test table discovery includes both schemas
            tables = await database.get_tables()
            test_schema_tables = [t for t in tables if t.startswith("test_schema.")]

            assert len(test_schema_tables) > 0, "Should discover tables in custom schema"
            assert "test_schema.multi_schema_table" in test_schema_tables

            # Test inspect table works with custom schema
            schema_info = await database.inspect_table("test_schema.multi_schema_table")
            assert len(schema_info) > 0

            column_names = schema_info["column_name"].tolist()
            assert "id" in column_names
            assert "name" in column_names

        finally:
            # Clean up
            try:
                await database.query("DROP TABLE test_schema.multi_schema_table")
                await database.query("DROP SCHEMA test_schema")
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_sqlserver_identity_columns(self, sqlserver_url):
        """Test SQL Server identity column handling."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        # Create table with identity column
        await database.query("""
            CREATE TABLE dbo.identity_test (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(50)
            )
        """)

        try:
            # Test that inspect_table shows identity column info
            schema_info = await database.inspect_table("dbo.identity_test")
            assert len(schema_info) > 0

            # Find the identity column
            id_column = schema_info[schema_info["column_name"] == "id"].iloc[0]
            assert id_column["data_type"].lower() == "int"

            # Test that we can sample from table with identity column
            sample = await database.sample_table("dbo.identity_test", n=1)
            assert len(sample) == 0  # Empty table

        finally:
            with contextlib.suppress(Exception):
                await database.query("DROP TABLE dbo.identity_test")

    @pytest.mark.asyncio
    async def test_sqlserver_connection_error_handling(self, sqlserver_url):
        """Test SQL Server connection error handling."""
        # Test with invalid database
        invalid_url = sqlserver_url.replace("/master", "/nonexistent_db")
        connection = Connection(url=invalid_url)
        database = await connection.connect()

        result = await database.test_connection()
        assert not result.connected, "Should fail to connect to non-existent database"
        assert "message" in result.__dict__, "Should provide error message"

    @pytest.mark.asyncio
    async def test_sqlserver_inspect_table_validation(self, sqlserver_url):
        """Test SQL Server table path validation in inspect_table."""
        connection = Connection(url=sqlserver_url)
        database = await connection.connect()

        # Test invalid table path formats
        invalid_paths = [
            "just_table_name",  # Missing schema
            "schema.table.extra",  # Too many parts
            "",  # Empty string
        ]

        for invalid_path in invalid_paths:
            with pytest.raises(ValueError, match="Invalid table path"):
                await database.inspect_table(invalid_path)
