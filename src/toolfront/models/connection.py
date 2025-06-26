"""
Data source abstraction layer for ToolFront.
"""

import importlib
import importlib.util
import logging
from typing import Any
from urllib.parse import unquote

from pydantic import BaseModel, Field
from sqlalchemy.engine.url import make_url

from toolfront.models.database import ConnectionResult, Database
from toolfront.models.databases import DatabaseType

logger = logging.getLogger("toolfront.connection")


class Connection(BaseModel):
    """Enhanced data source with smart path resolution."""

    url: str = Field(..., description="URL of the data source with protocol.")

    async def connect(self, url_map: dict[str, Any] | None = None) -> Database:
        """Get the appropriate connector for this data source
        Args:
            url_map: A dictionary mapping obfuscated URL strings to original URLs
        """
        # Get the original URL, considering URL mapping
        original_url = url_map[self.url] if url_map and self.url in url_map else self.url

        # Handle URL parsing correctly without losing password info
        if isinstance(original_url, str):
            original_url = unquote(original_url)
        else:
            # If it's already a URL object, use render to preserve credentials
            original_url = original_url.render_as_string(hide_password=False)

        # Parse the URL
        url = make_url(original_url)

        # Standard connection
        return self._create_database(url)

    def _create_database(self, url) -> Database:
        """Create a database instance without SSH tunnel."""
        db_map = {
            "bigquery": (DatabaseType.BIGQUERY, "BigQuery"),
            "databricks": (DatabaseType.DATABRICKS, "Databricks"),
            "duckdb": (DatabaseType.DUCKDB, "DuckDB"),
            "mysql": (DatabaseType.MYSQL, "MySQL"),
            "postgresql": (DatabaseType.POSTGRESQL, "PostgreSQL"),
            "postgres": (DatabaseType.POSTGRESQL, "PostgreSQL"),
            "snowflake": (DatabaseType.SNOWFLAKE, "Snowflake"),
            "sqlite": (DatabaseType.SQLITE, "SQLite"),
            "mssql": (DatabaseType.SQLSERVER, "SQLServer"),
            "sqlserver": (DatabaseType.SQLSERVER, "SQLServer"),
        }

        driver_name = url.drivername
        if driver_name not in db_map:
            raise ValueError(f"Unsupported data source: {driver_name}")

        db_type, db_class_name = db_map[driver_name]

        module = importlib.import_module(f"toolfront.models.databases.{db_type.value}")
        db_class = getattr(module, db_class_name)

        # Set the correct async driver for certain databases
        if db_type == DatabaseType.MYSQL:
            if not importlib.util.find_spec("aiomysql"):
                raise ImportError(
                    "Missing dependencies for MySQL. Please install them using: pip install 'toolfront[mysql]'"
                )
            url = url.set(drivername="mysql+aiomysql")
        elif db_type == DatabaseType.POSTGRESQL:
            if not importlib.util.find_spec("asyncpg"):
                raise ImportError(
                    "Missing dependencies for PostgreSQL. "
                    "Please install them using: pip install 'toolfront[postgresql]'"
                )
            url = url.set(drivername=f"{driver_name}+asyncpg")
        elif db_type == DatabaseType.SQLITE:
            if not importlib.util.find_spec("aiosqlite"):
                raise ImportError(
                    "Missing dependencies for SQLite. Please install them using: pip install 'toolfront[sqlite]'"
                )
            url = url.set(drivername="sqlite+aiosqlite")
        elif db_type == DatabaseType.SQLSERVER:
            if not importlib.util.find_spec("pyodbc"):
                raise ImportError(
                    "Missing dependencies for SQLServer. Please install them using: pip install 'toolfront[sqlserver]'"
                )
            url = url.set(drivername="mssql+pyodbc")

        return db_class(url=url)

    async def test_connection(self) -> ConnectionResult:
        """Test database connection"""
        try:
            db = await self.connect()
            return await db.test_connection()
        except ImportError as e:
            return ConnectionResult(connected=False, message=str(e))
