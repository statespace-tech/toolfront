import importlib
import importlib.util
import logging
from typing import Any

from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.engine.url import URL, make_url

from toolfront.models.api import API
from toolfront.models.database import ConnectionResult, Database
from toolfront.models.databases import DatabaseType

logger = logging.getLogger("toolfront.connection")


class Connection(BaseModel):
    """Connection to a data source."""

    async def connect(self, url_map: dict[str, Any]) -> Database | API:
        """Connect to the data source."""
        raise NotImplementedError("Subclasses must implement connect")

    async def test_connection(self, url_map: dict[str, Any]) -> ConnectionResult:
        """Test the connection to the data source."""
        raise NotImplementedError("Subclasses must implement test_connection")

    @classmethod
    def from_url(cls, url: str) -> "Connection":
        """Create a connection from a URL."""
        if url.startswith("http"):
            return APIConnection(url=url)
        else:
            return DatabaseConnection(url=url)


class APIConnection(Connection):
    """API connection."""

    url: str = Field(..., description="Full URL of the API.")

    async def connect(self, url_map: dict[str, Any]) -> API:
        """Connect to the API."""
        # Get the OpenAPI spec from the URL map
        extra = url_map.get(self.url, {}).get("extra", {})
        return API(url=self.url, **extra)

    async def test_connection(self, url_map: dict[str, Any]) -> ConnectionResult:
        """Test database connection"""
        try:
            api = await self.connect(url_map=url_map)
            return await api.test_connection()
        except ImportError as e:
            return ConnectionResult(connected=False, message=str(e))


class DatabaseConnection(Connection):
    """Enhanced data source with smart path resolution."""

    url: SecretStr = Field(..., description="Full URL of the database.")

    async def connect(self, url_map: dict[str, Any] | None = None) -> Database:
        """Get the appropriate connector for this data source"""
        # Get the actual secret value for connection
        actual_url = self.url.get_secret_value()
        url = make_url(actual_url)
        return self._create_database(url)

    def _create_database(self, url: URL) -> Database:
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
                raise ImportError("Missing dependencies for MySQL. Please install them using: uvx 'toolfront[mysql]'")
            url = url.set(drivername="mysql+aiomysql")
        elif db_type == DatabaseType.POSTGRESQL:
            if not importlib.util.find_spec("asyncpg"):
                raise ImportError(
                    "Missing dependencies for PostgreSQL. Please install them using: uvx 'toolfront[postgresql]'"
                )
            url = url.set(drivername=f"{driver_name}+asyncpg")
        elif db_type == DatabaseType.SQLITE:
            if not importlib.util.find_spec("aiosqlite"):
                raise ImportError("Missing dependencies for SQLite. Please install them using: uvx 'toolfront[sqlite]'")
            url = url.set(drivername="sqlite+aiosqlite")
        elif db_type == DatabaseType.SQLSERVER:
            if not importlib.util.find_spec("pyodbc"):
                raise ImportError(
                    "Missing dependencies for SQLServer. Please install them using: uvx 'toolfront[sqlserver]'"
                )
            url = url.set(drivername="mssql+pyodbc")

        return db_class(url=url)

    async def test_connection(self, url_map: dict[str, Any]) -> ConnectionResult:
        """Test database connection"""
        try:
            db = await self.connect(url_map=url_map)
            return await db.test_connection()
        except ImportError as e:
            return ConnectionResult(connected=False, message=str(e))
