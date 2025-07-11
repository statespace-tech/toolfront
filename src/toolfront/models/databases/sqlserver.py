import pandas as pd

from toolfront.cache import cache
from toolfront.config import CACHE_TTL
from toolfront.models.database import Database, SQLAlchemyMixin


class SQLServer(SQLAlchemyMixin, Database):
    """SQL Server connection manager with utility functions."""

    def initialize_session(self) -> str:
        return "SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"

    @cache(expire=CACHE_TTL)
    async def get_tables(self) -> list[str]:
        """Get both tables and views from SQL Server."""
        query = """
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'sys', 'INFORMATION_SCHEMA', 'SYS')
            AND table_type IN ('BASE TABLE', 'VIEW')
            ORDER BY table_schema, table_name;
        """
        data = await self.query(code=query)
        # Use positional access to avoid driver-specific column naming inconsistencies
        return data.apply(lambda x: f"{x.iloc[0]}.{x.iloc[1]}", axis=1).tolist()

    async def inspect_table(self, table_path: str) -> pd.DataFrame:
        """Inspect the structure of a table or view."""
        splits = table_path.split(".")

        if not len(splits) == 2:
            raise ValueError(f"Invalid table path: {table_path}. Expected format: schema.table")

        table_schema, table_name = splits

        try:
            code = f"""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    ordinal_position,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_schema = '{table_schema}'
                AND table_name = '{table_name}'
                ORDER BY ordinal_position;
            """

            result = await self.query(code=code)
            if result.empty:
                raise ValueError(f"Table or view '{table_path}' not found or has no columns")

            return result

        except Exception as e:
            raise ValueError(f"Failed to inspect table '{table_path}': {str(e)}") from e

    async def sample_table(self, table_path: str, n: int = 5) -> pd.DataFrame:
        """Sample data from a table or view using SQL Server TOP syntax."""
        splits = table_path.split(".")

        if not len(splits) == 2:
            raise ValueError(f"Invalid table path: {table_path}. Expected format: schema.table")

        if n <= 0:
            raise ValueError(f"Sample size must be positive, got {n}")

        try:
            return await self.query(code=f"SELECT TOP {n} * FROM [{splits[0]}].[{splits[1]}]")
        except Exception as e:
            raise ValueError(f"Failed to sample table '{table_path}': {str(e)}") from e
