import importlib
import importlib.util
import logging

from pydantic import Field
from sqlalchemy.engine.url import URL, make_url

from toolfront.models.connection import Connection
from toolfront.models.database import Database
from toolfront.models.databases import DatabaseType, db_map

logger = logging.getLogger("toolfront")


class DatabaseConnection(Connection):
    url: str = Field(..., description="Full database URL.")

    async def connect(self) -> Database:
        from toolfront.cache import load_from_env

        # Load the actual connection URL and validate it
        url: URL = make_url(load_from_env(self.url))

        drivername = url.drivername
        if drivername not in db_map:
            raise ValueError(f"Unsupported data source: {drivername}")

        db_type, db_class_name = db_map[drivername]

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
            url = url.set(drivername=f"{drivername}+asyncpg")
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

        # Create and return the database instance
        module = importlib.import_module(f"toolfront.models.databases.{db_type.value}")
        db_class = getattr(module, db_class_name)
        return db_class(url=url)
