"""
Data source abstraction layer for ToolFront.
"""

import logging
from typing import Any
from urllib.parse import unquote

from pydantic import BaseModel, Field
from sqlalchemy.engine.url import make_url

from toolfront.models.database import ConnectionResult, Database
from toolfront.models.databases import (
    BigQuery,
    Databricks,
    DuckDB,
    MySQL,
    PostgreSQL,
    Snowflake,
    SQLite,
    SQLServer,
)

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
        if url.drivername == "bigquery":
            return BigQuery(url=url)
        elif url.drivername == "databricks":
            return Databricks(url=url)
        elif url.drivername == "duckdb":
            return DuckDB(url=url)
        elif url.drivername == "mysql":
            return MySQL(url=url.set(drivername="mysql+aiomysql"))
        elif url.drivername == "postgresql":
            return PostgreSQL(url=url.set(drivername="postgresql+asyncpg"))
        elif url.drivername == "snowflake":
            return Snowflake(url=url)
        elif url.drivername == "sqlite":
            return SQLite(url=url.set(drivername="sqlite+aiosqlite"))
        elif url.drivername in ("mssql", "sqlserver"):
            return SQLServer(url=url.set(drivername="mssql+pyodbc"))
        else:
            raise ValueError(f"Unsupported data source: {url}")

    async def test_connection(self) -> ConnectionResult:
        """Test database connection"""
        db = await self.connect()
        return await db.test_connection()
