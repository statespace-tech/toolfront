import pandas as pd

from toolfront.cache import cache
from toolfront.config import CACHE_TTL
from toolfront.models.database import Database, SQLAlchemyMixin


class PostgreSQL(SQLAlchemyMixin, Database):
    """PostgreSQL connection manager with utility functions."""

    def initialize_session(self) -> str:
        return "SET TRANSACTION READ ONLY"

    @cache(expire=CACHE_TTL)
    async def get_tables(self) -> list[str]:
        code = """
            SELECT table_schema, table_name 
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """
        data = await self.query(code)
        # Use positional access instead of column names to avoid driver-specific naming inconsistencies.
        # x.iloc[0] = table_schema (first column), x.iloc[1] = table_name (second column)
        # Different PostgreSQL drivers (asyncpg vs psycopg2) may handle column naming differently.
        return data.apply(lambda x: f"{x.iloc[0]}.{x.iloc[1]}", axis=1).tolist()

    async def inspect_table(self, table_path: str) -> pd.DataFrame:
        splits = table_path.split(".")

        if not len(splits) == 2:
            raise ValueError(f"Invalid table path: {table_path}. Expected format: schema.table")

        table_schema, table_name = splits

        code = f"""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    ordinal_position
                FROM information_schema.columns
                WHERE table_schema = '{table_schema}' 
                AND table_name = '{table_name}'
                ORDER BY ordinal_position;
        """

        return await self.query(code)

    async def sample_table(self, table_path: str, n: int = 5) -> pd.DataFrame:
        return await self.query(f"SELECT * FROM {table_path} LIMIT {n};")
