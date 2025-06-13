"""Databricks integration for Toolfront."""

import logging

import pandas as pd
from async_lru import alru_cache

from toolfront.config import ALRU_CACHE_TTL
from toolfront.models.database import ConnectionResult, Database, DatabaseError, MatchMode

logger = logging.getLogger("toolfront")


class Databricks(Database):
    """Databricks connection manager."""

    async def test_connection(self) -> ConnectionResult:
        """Test database connection."""
        try:
            await self.query("SELECT 1 as test")
            return ConnectionResult(connected=True, message="Connection successful")
        except Exception as e:
            return ConnectionResult(connected=False, message=f"Connection failed: {e}")

    def _extract_token(self) -> str:
        """Extract authentication token from URL."""
        # Username/password format: databricks://token:actual_token@host
        if self.url.username == "token" and self.url.password:
            return self.url.password

        # Query parameter formats
        return (
            self.url.query.get("token")
            or self.url.query.get("access_token")
            or self.url.query.get("personal_access_token")
            or ""
        )

    async def query(self, code: str) -> pd.DataFrame:
        """Execute SQL query using Databricks SQL connector."""
        try:
            from databricks import sql
        except ImportError:
            raise DatabaseError("databricks-sql-connector package is required for Databricks integration")

        hostname = self.url.host
        http_path = self.url.query.get("http_path", "")
        token = self._extract_token()

        if not http_path or not token:
            raise ValueError("http_path and token are required in the URL")

        logger.debug(f"Connecting to Databricks: hostname={hostname}")

        try:
            with (
                sql.connect(
                    server_hostname=hostname, http_path=http_path, access_token=token, _timeout=30
                ) as connection,
                connection.cursor() as cursor,
            ):
                cursor.execute(code)
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    data = cursor.fetchall()
                    return pd.DataFrame(data, columns=columns)
                return pd.DataFrame()
        except Exception as e:
            raise DatabaseError(f"Query execution failed: {e}")

    def _format_table_names(self, data: pd.DataFrame) -> list[str]:
        """Format table names from query results."""
        if data.empty:
            return []

        columns = data.columns.tolist()

        # Standard Databricks formats
        if "database" in columns and "tableName" in columns:
            return [f"{row['database']}.{row['tableName']}" for _, row in data.iterrows()]
        elif "databaseName" in columns and "tableName" in columns:
            return [f"{row['databaseName']}.{row['tableName']}" for _, row in data.iterrows()]
        elif len(columns) >= 2:
            return [f"{row[0]}.{row[1]}" for _, row in data.iterrows()]
        else:
            logger.warning("Couldn't determine table name format, returning raw table names")
            return [str(row[0]) for _, row in data.iterrows()]

    @alru_cache(maxsize=None, ttl=ALRU_CACHE_TTL)
    async def get_tables(self) -> list[str]:
        """Get list of all tables in all catalogs and schemas."""
        try:
            data = await self.query("SHOW TABLES")
            return self._format_table_names(data)
        except Exception as first_error:
            logger.warning(f"SHOW TABLES failed: {first_error}, trying information_schema")

            try:
                query = """
                    SELECT table_catalog, table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE'
                    ORDER BY table_catalog, table_schema, table_name
                """
                data = await self.query(query)

                if data.empty:
                    return []

                return [f"{row[0]}.{row[1]}.{row[2]}" for _, row in data.iterrows()]

            except Exception as second_error:
                logger.error(f"Both table listing methods failed: {first_error}, {second_error}")
                raise DatabaseError(f"Failed to get tables from Databricks: {second_error}") from second_error

    async def scan_tables(self, pattern: str, mode: MatchMode = MatchMode.REGEX, limit: int = 10) -> list[str]:
        """Match table names using different algorithms."""
        try:
            table_names = await self.get_tables()
            if not table_names:
                return []

            scan_methods = {
                MatchMode.REGEX: self._scan_tables_regex,
                MatchMode.JARO_WINKLER: self._scan_tables_jaro_winkler,
                MatchMode.TF_IDF: self._scan_tables_tf_idf,
            }

            scan_method = scan_methods.get(mode, self._scan_tables_regex)
            if mode not in scan_methods:
                logger.warning(f"Unknown match mode: {mode}, falling back to regex")

            return scan_method(table_names, pattern, limit)

        except Exception as e:
            logger.error(f"Table scan failed for Databricks: {e}")
            raise DatabaseError(f"Failed to scan tables in Databricks: {e}") from e

    def _get_detailed_table_info(self, catalog: str, schema: str, table: str) -> str:
        """Build information_schema query for table inspection."""
        return f"""
            SELECT column_name, data_type, is_nullable, column_default, ordinal_position
            FROM {catalog}.information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
        """

    async def inspect_table(self, table_path: str) -> pd.DataFrame:
        """Get schema information for the specified table."""
        if not table_path:
            raise ValueError(f"Invalid table path: {table_path}")

        splits = table_path.split(".")

        try:
            if len(splits) == 3:
                catalog, schema, table = splits
                try:
                    query = self._get_detailed_table_info(catalog, schema, table)
                    return await self.query(query)
                except Exception as e:
                    logger.warning(f"Failed to inspect using information_schema: {e}")
                    return await self.query(f"DESCRIBE TABLE {table_path}")
            elif len(splits) == 2:
                return await self.query(f"DESCRIBE TABLE {table_path}")
            else:
                raise ValueError(f"Invalid table path: {table_path}. Expected format: [catalog.]schema.table")

        except Exception as e:
            logger.error(f"Failed to inspect table {table_path}: {e}")
            raise DatabaseError(f"Failed to inspect table {table_path}: {e}") from e

    async def sample_table(self, table_path: str, n: int = 5) -> pd.DataFrame:
        """Get sample rows from the specified table."""
        if not table_path or not isinstance(table_path, str):
            raise ValueError(f"Invalid table path: {table_path}")

        if "." not in table_path and "`" not in table_path:
            logger.warning(f"Table path doesn't contain schema: {table_path}")

        try:
            return await self.query(f"SELECT * FROM {table_path} LIMIT {n}")
        except Exception as limit_error:
            logger.warning(f"LIMIT failed: {limit_error}, trying TABLESAMPLE")

            try:
                return await self.query(f"SELECT * FROM {table_path} TABLESAMPLE ({n} ROWS)")
            except Exception as sample_error:
                logger.warning(f"TABLESAMPLE failed: {sample_error}, retrying LIMIT")
                try:
                    return await self.query(f"SELECT * FROM {table_path} LIMIT {n}")
                except Exception as e:
                    logger.error(f"Failed to sample table {table_path}: {e}")
                    raise DatabaseError(f"Failed to sample table {table_path}: {e}") from e
