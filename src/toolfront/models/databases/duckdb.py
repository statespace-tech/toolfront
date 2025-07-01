from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from toolfront.models.database import ConnectionResult, Database, FileMixin

EXTENSIONS = ["csv", "json", "xlsx", "parquet"]


class DuckDB(FileMixin, Database):
    """DuckDB connection manager with utility functions."""

    async def test_connection(self) -> ConnectionResult:
        """Test the connection to the DuckDB database."""
        try:
            # In memory databases cannot be read only
            read_only = self.url.database != ":memory:"
            with duckdb.connect(self.url.database or ":memory:", read_only=read_only) as conn:
                conn.sql("SELECT 1")
                return ConnectionResult(connected=True, message="Connection successful")
        except Exception as e:
            return ConnectionResult(connected=False, message=f"Connection failed: {e}")

    async def query(self, code: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        with duckdb.connect(self.url.database or ":memory:") as conn:
            return conn.sql(code).df()

    async def get_tables(self) -> Any:
        """Get all available tables (both database tables and filesystem files)."""
        return await self._get_db_tables() + await self._get_filesystem_tables()

    async def inspect_table(self, table_path: str) -> pd.DataFrame:
        """Inspect a table schema.

        Args:
            table_path: Path to table (file path for files, schema.table for DB tables)

        Returns:
            DataFrame with table schema information
        """
        if any(table_path.endswith(f".{ext}") for ext in EXTENSIONS):
            return await self._inspect_filesystem_table(table_path)
        else:
            return await self._inspect_db_table(table_path)

    async def sample_table(self, table_path: str, n: int = 5) -> Any:
        """Sample data from a table.

        Args:
            table_path: Path to table (file path for files, schema.table for DB tables)
            n: Number of rows to sample

        Returns:
            DataFrame with sampled data
        """
        if any(table_path.endswith(f".{ext}") for ext in EXTENSIONS):
            return await self._sample_filesystem_table(table_path, n)
        else:
            return await self._sample_db_table(table_path, n)

    async def _get_filesystem_tables(self, exclude_hidden: bool = True) -> Any:
        """Get all supported files from the filesystem recursively."""
        all_files = []

        for ext in EXTENSIONS:
            matching_files = list(Path().rglob(f"*.{ext}"))
            all_files.extend([str(f) for f in matching_files if not exclude_hidden or not str(f).startswith(".")])

        return all_files

    async def _inspect_filesystem_table(self, table_path: str) -> pd.DataFrame:
        """Inspect schema of a file-based table."""
        return await self.query(f"DESCRIBE SELECT * FROM {self._duckdb_read_function_command(table_path)}")

    async def _sample_filesystem_table(self, table_path: str, n: int = 5) -> pd.DataFrame:
        """Sample data from a file-based table."""
        return await self.query(f"SELECT * FROM {self._duckdb_read_function_command(table_path)} USING SAMPLE {n} ROWS")

    async def _get_db_tables(self) -> list[str]:
        """Get all table names in the DuckDB database."""
        code = """
            SELECT table_schema, table_name 
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """
        data = await self.query(code)
        return data.apply(lambda x: f"{x['table_schema']}.{x['table_name']}", axis=1).tolist()

    async def _inspect_db_table(self, table_path: str) -> pd.DataFrame:
        """Inspect schema of a database table."""
        # Handle both "table" and "schema.table" formats
        if "." in table_path:
            schema_name, table_name = table_path.split(".", 1)
        else:
            schema_name, table_name = "main", table_path

        code = f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND table_schema = '{schema_name}'
        """
        return await self.query(code)

    async def _sample_db_table(self, table_path: str, n: int = 5) -> pd.DataFrame:
        """Sample data from a database table."""
        # Handle both "table" and "schema.table" formats
        if "." in table_path:
            schema_name, table_name = table_path.split(".", 1)
        else:
            schema_name, table_name = "main", table_path

        code = f"""
            SELECT * FROM {schema_name}.{table_name}
            USING SAMPLE {n} ROWS
        """
        return await self.query(code)

    def _duckdb_read_function_command(self, filepath: str) -> str:
        """Generate the appropriate DuckDB read function for a given file path."""
        extension = filepath.split(".")[-1]
        if extension == "csv":
            return f"read_csv_auto('{filepath}')"
        elif extension == "json":
            return f"read_json_auto('{filepath}')"
        elif extension == "xlsx":
            return f"read_xlsx('{filepath}')"
        elif extension == "parquet":
            return f"read_parquet('{filepath}')"
        else:
            raise ValueError(f"Unsupported file extension: {filepath}")
