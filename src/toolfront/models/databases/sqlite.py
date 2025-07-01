from typing import Any

import pandas as pd

from toolfront.models.database import Database, FileMixin, SQLAlchemyMixin


class SQLite(SQLAlchemyMixin, FileMixin, Database):
    def initialize_session(self) -> str:
        return "PRAGMA query_only = ON"

    async def get_tables(self) -> list[str]:
        data = await self.query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        )
        if not len(data):
            return []
        return data["name"].tolist()

    async def inspect_table(self, table_path: str) -> pd.DataFrame:
        return await self.query(f"PRAGMA table_info('{table_path}')")

    async def sample_table(self, table_path: str, n: int = 5) -> Any:
        return await self.query(f"SELECT * FROM {table_path} LIMIT {n}")
