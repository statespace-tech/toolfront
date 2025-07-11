from typing import Any

import pandas as pd

from toolfront.cache import cache
from toolfront.config import CACHE_TTL
from toolfront.models.database import Database, SQLAlchemyMixin


class MySQL(SQLAlchemyMixin, Database):
    """MySQL connection manager with utility functions."""

    def initialize_session(self) -> str:
        return "SET SESSION TRANSACTION READ ONLY"

    @cache(expire=CACHE_TTL)
    async def get_tables(self) -> list[str]:
        code = """
            SELECT table_schema, table_name 
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """
        data = await self.query(code)
        # Use positional access instead of column names to avoid driver-specific naming inconsistencies.
        # x.iloc[0] = table_schema (first column), x.iloc[1] = table_name (second column)
        # Different MySQL drivers (aiomysql vs pymysql) may handle column naming differently.
        return data.apply(lambda x: f"{x.iloc[0]}.{x.iloc[1]}", axis=1).tolist()

    async def inspect_table(self, table_path: str) -> pd.DataFrame:
        schema_name, table_name = table_path.split(".")

        return await self.query(f"SHOW FULL COLUMNS FROM `{schema_name}`.`{table_name}`;")

    async def sample_table(self, table_path: str, n: int = 5) -> Any:
        return await self.query(f"SELECT * FROM {table_path} ORDER BY RAND() LIMIT {n};")
