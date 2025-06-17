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
from toolfront.ssh import SSHConfig, SSHTunnelManager, extract_ssh_params

logger = logging.getLogger("toolfront.connection")


class SSHTunnelDatabase(BaseModel):
    """Wrapper for database connections through SSH tunnels."""

    database: Database
    tunnel_manager: SSHTunnelManager

    class Config:
        arbitrary_types_allowed = True

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        # Tunnel cleanup is handled by the tunnel manager context
        pass


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
        original_url = unquote(original_url) if isinstance(original_url, str) else str(original_url)

        # Extract SSH parameters if present
        clean_url, ssh_config = extract_ssh_params(original_url)

        # Parse the clean URL
        url = make_url(clean_url)

        # If SSH tunnel is needed, modify the URL to use localhost
        if ssh_config:
            logger.info(f"SSH tunnel detected for {url.drivername} connection")
            # We'll create a special database wrapper that manages the tunnel
            return await self._create_ssh_database(url, ssh_config)

        # Standard connection without SSH tunnel
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

    async def _create_ssh_database(self, url, ssh_config: SSHConfig) -> Database:
        """Create a database instance with SSH tunnel support."""
        # Only PostgreSQL and MySQL support SSH tunnels for now
        if url.drivername not in ("postgresql", "mysql"):
            raise ValueError(f"SSH tunnels are not yet supported for {url.drivername}")

        # Create the database with a placeholder tunnel URL
        # The actual tunnel connection will be handled by the database class
        tunnel_db = SSHTunnelledDatabase(url=url, ssh_config=ssh_config)
        return tunnel_db

    async def test_connection(self) -> ConnectionResult:
        """Test database connection"""
        db = await self.connect()
        return await db.test_connection()


class SSHTunnelledDatabase(Database):
    """Database connection that uses SSH tunneling."""

    ssh_config: SSHConfig = Field(..., description="SSH tunnel configuration")
    _actual_database: Database | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def _tunnel_manager(self) -> SSHTunnelManager:
        """Get the SSH tunnel manager."""
        if not hasattr(self, "_cached_tunnel_manager"):
            self._cached_tunnel_manager = SSHTunnelManager(self.ssh_config)
        return self._cached_tunnel_manager

    async def _get_tunnelled_database(self) -> Database:
        """Get the actual database connection through SSH tunnel."""
        if self._actual_database is not None:
            return self._actual_database

        # This will be handled by context managers in the actual database operations
        raise RuntimeError("Direct access to tunnelled database not supported. Use async context methods.")

    async def test_connection(self) -> ConnectionResult:
        """Test the connection through SSH tunnel."""
        try:
            async with self._tunnel_manager.tunnel() as local_port:
                # Create a tunnelled URL pointing to localhost
                tunnelled_url = self.url.set(host="localhost", port=local_port)

                # Create the actual database connection
                if self.url.drivername == "postgresql":
                    from toolfront.models.databases.postgresql import PostgreSQL

                    db = PostgreSQL(url=tunnelled_url.set(drivername="postgresql+asyncpg"))
                elif self.url.drivername == "mysql":
                    from toolfront.models.databases.mysql import MySQL

                    db = MySQL(url=tunnelled_url.set(drivername="mysql+aiomysql"))
                else:
                    raise ValueError(f"SSH tunnels not supported for {self.url.drivername}")

                return await db.test_connection()

        except Exception as e:
            logger.error(f"SSH tunnel connection test failed: {e}")
            return ConnectionResult(connected=False, message=f"SSH tunnel connection failed: {e}")

    async def get_tables(self) -> list[str]:
        """Get tables through SSH tunnel."""
        async with self._tunnel_manager.tunnel() as local_port:
            tunnelled_url = self.url.set(host="localhost", port=local_port)

            if self.url.drivername == "postgresql":
                from toolfront.models.databases.postgresql import PostgreSQL

                db = PostgreSQL(url=tunnelled_url.set(drivername="postgresql+asyncpg"))
            elif self.url.drivername == "mysql":
                from toolfront.models.databases.mysql import MySQL

                db = MySQL(url=tunnelled_url.set(drivername="mysql+aiomysql"))
            else:
                raise ValueError(f"SSH tunnels not supported for {self.url.drivername}")

            return await db.get_tables()

    async def inspect_table(self, table_path: str):
        """Inspect table structure through SSH tunnel."""
        async with self._tunnel_manager.tunnel() as local_port:
            tunnelled_url = self.url.set(host="localhost", port=local_port)

            if self.url.drivername == "postgresql":
                from toolfront.models.databases.postgresql import PostgreSQL

                db = PostgreSQL(url=tunnelled_url.set(drivername="postgresql+asyncpg"))
            elif self.url.drivername == "mysql":
                from toolfront.models.databases.mysql import MySQL

                db = MySQL(url=tunnelled_url.set(drivername="mysql+aiomysql"))
            else:
                raise ValueError(f"SSH tunnels not supported for {self.url.drivername}")

            return await db.inspect_table(table_path)

    async def sample_table(self, table_path: str, n: int = 5):
        """Sample table data through SSH tunnel."""
        async with self._tunnel_manager.tunnel() as local_port:
            tunnelled_url = self.url.set(host="localhost", port=local_port)

            if self.url.drivername == "postgresql":
                from toolfront.models.databases.postgresql import PostgreSQL

                db = PostgreSQL(url=tunnelled_url.set(drivername="postgresql+asyncpg"))
            elif self.url.drivername == "mysql":
                from toolfront.models.databases.mysql import MySQL

                db = MySQL(url=tunnelled_url.set(drivername="mysql+aiomysql"))
            else:
                raise ValueError(f"SSH tunnels not supported for {self.url.drivername}")

            return await db.sample_table(table_path, n)

    async def query(self, code: str):
        """Execute query through SSH tunnel."""
        async with self._tunnel_manager.tunnel() as local_port:
            tunnelled_url = self.url.set(host="localhost", port=local_port)

            if self.url.drivername == "postgresql":
                from toolfront.models.databases.postgresql import PostgreSQL

                db = PostgreSQL(url=tunnelled_url.set(drivername="postgresql+asyncpg"))
            elif self.url.drivername == "mysql":
                from toolfront.models.databases.mysql import MySQL

                db = MySQL(url=tunnelled_url.set(drivername="mysql+aiomysql"))
            else:
                raise ValueError(f"SSH tunnels not supported for {self.url.drivername}")

            return await db.query(code)
