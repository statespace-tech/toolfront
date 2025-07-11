import pandas as pd

from toolfront.cache import cache
from toolfront.config import CACHE_TTL
from toolfront.models.database import Database, DatabaseError, SQLAlchemyMixin


class Snowflake(SQLAlchemyMixin, Database):
    @cache(expire=CACHE_TTL)
    async def get_tables(self) -> list[str]:
        """For Snowflake, this method returns both tables and views combined"""
        try:
            # Get both tables and views
            tables_code = "SHOW TABLES IN ACCOUNT;"
            views_code = "SHOW VIEWS IN ACCOUNT;"

            tables_data = await self.query(tables_code)
            views_data = await self.query(views_code)

            # Comb?ine the results
            combined_data = pd.DataFrame()

            if tables_data is not None and not tables_data.empty:
                combined_data = pd.concat([combined_data, tables_data], ignore_index=True)

            if views_data is not None and not views_data.empty:
                combined_data = pd.concat([combined_data, views_data], ignore_index=True)

            if combined_data.empty:
                return []

            return combined_data.apply(
                lambda x: f"{x['database_name']}.{x['schema_name']}.{x['name']}", axis=1
            ).tolist()
        except Exception as e:
            raise DatabaseError(f"Failed to get tables and views from Snowflake: {e}") from e

    async def inspect_table(self, table_path: str) -> pd.DataFrame:
        return await self.query(f"DESCRIBE TABLE {table_path}")

    async def sample_table(self, table_path: str, n: int = 5) -> pd.DataFrame:
        return await self.query(f"SELECT * FROM {table_path} TABLESAMPLE BERNOULLI ({n} ROWS);")
