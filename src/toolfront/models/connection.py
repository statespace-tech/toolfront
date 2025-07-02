import importlib
import importlib.util
import logging
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.engine.url import URL, make_url

from toolfront.models.api import API
from toolfront.models.database import ConnectionResult, Database
from toolfront.models.databases import DatabaseType
from toolfront.models.url import APIURL, DatabaseURL

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
    def from_url(cls, url: str, url_map: dict[Any, Any] | None = None, **kwargs) -> "Connection":
        """Create a connection from a URL."""
        if url.startswith("http"):
            # For API URLs, we might need additional auth info
            auth_headers = kwargs.get("auth_headers", {})
            auth_query_params = kwargs.get("auth_query_params", {})
            query_params = kwargs.get("query_params", {})
            api_url = APIURL.from_url_string(url, auth_headers, auth_query_params, query_params)
            return APIConnection(url=api_url)
        else:
            # Check if this is a display URL that needs to be resolved
            if url_map and "***" in url:
                # This is a display URL, find the actual structured URL object
                for url_obj in url_map:
                    if str(url_obj) == url:  # Match display string
                        return DatabaseConnection(url=url_obj)

            # Parse as new URL
            db_url = DatabaseURL.from_url_string(url)
            return DatabaseConnection(url=db_url)


class APIConnection(Connection):
    """API connection."""

    url: APIURL = Field(..., description="Structured API URL.")

    async def connect(self, url_map: dict[str, Any]) -> API:
        """Connect to the API."""
        # Use display string (base URL without auth params) for the API URL
        base_url = self.url.to_display_string()
        # Extract auth parameters from the structured URL
        auth_headers = {k: v.get_secret_value() for k, v in self.url.auth_headers.items()}
        auth_query_params = {k: v.get_secret_value() for k, v in self.url.auth_query_params.items()}

        # Get OpenAPI spec from metadata if available
        openapi_spec = None
        if hasattr(self, "_metadata") and self._metadata:
            extra = self._metadata.get("extra", {})
            openapi_spec = extra.get("openapi_spec")

        return API(
            url=base_url, auth_headers=auth_headers, auth_query_params=auth_query_params, openapi_spec=openapi_spec
        )

    async def test_connection(self, url_map: dict[str, Any]) -> ConnectionResult:
        """Test database connection"""
        try:
            api = await self.connect(url_map=url_map)
            return await api.test_connection()
        except ImportError as e:
            return ConnectionResult(connected=False, message=str(e))


class DatabaseConnection(Connection):
    """Enhanced data source with smart path resolution."""

    url: DatabaseURL = Field(..., description="Structured database URL.")

    async def connect(self, url_map: dict[str, Any] | None = None) -> Database:
        """Get the appropriate connector for this data source"""
        # Get the actual connection string
        connection_string = self.url.to_connection_string()
        url = make_url(connection_string)
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
