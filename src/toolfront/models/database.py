import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.exc import InvalidRequestError, StatementError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.util import immutabledict

from toolfront.types import ConnectionResult, SearchMode
from toolfront.utils import search_items

try:
    from sqlalchemy.exc import MissingGreenlet
except ImportError:
    # MissingGreenlet might not be available in all SQLAlchemy versions
    class MissingGreenlet(Exception):  # type: ignore[no-redef]
        pass


logger = logging.getLogger("toolfront")


class DatabaseError(Exception):
    """Exception for database-related errors."""

    pass


class FileMixin:
    @field_validator("url", mode="after")
    def check_file_exists(cls, url: URL) -> URL:
        if url.database and not Path(url.database).is_file() and "memory:" not in url.database:
            raise DatabaseError(f"File does not exist: {url.database}")
        return url


class SQLAlchemyMixin:
    # Type annotation for mixed-in url attribute
    if TYPE_CHECKING:
        url: URL

    def initialize_session(self) -> str | None:
        """Return SQL statement to execute for session initialization, or None if no initialization needed."""
        return None

    async def test_connection(self) -> ConnectionResult:
        """Test the connection to the database."""
        try:
            await self.query("SELECT 1")
            return ConnectionResult(connected=True, message="Connection successful")
        except Exception as e:
            return ConnectionResult(connected=False, message=f"Connection failed: {e}")

    async def query(self, code: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        init_sql = self.initialize_session()

        # Try async first, fallback to sync for configuration errors
        try:
            return await self._execute_async(code, init_sql)
        except (InvalidRequestError, StatementError) as config_error:
            logger.debug(f"Async failed due to configuration, trying sync: {config_error}")
            return await self._execute_sync(code, init_sql, config_error)
        except Exception as async_error:
            # Check for greenlet-related errors or asyncpg authentication errors
            if self._is_greenlet_error(async_error) or self._is_asyncpg_auth_error(async_error):
                logger.debug(f"Async failed due to greenlet/auth issue, trying sync: {async_error}")
                return await self._execute_sync(code, init_sql, async_error)
            else:
                logger.error(f"Query failed: {async_error}")
                raise DatabaseError(f"Query execution failed: {async_error}") from async_error

    async def _execute_async(self, code: str, init_sql: str | None) -> pd.DataFrame:
        """Execute query using async engine."""
        engine = create_async_engine(self.url, echo=False)
        try:
            async with engine.connect() as conn:
                conn = await conn.execution_options(readonly=True)
                if init_sql:
                    await conn.execute(text(init_sql))
                result = await conn.execute(text(code))
                data = result.fetchall()
                logger.debug(f"Async query executed successfully: {code[:100]}...")
                return pd.DataFrame(data)  # .fillna('N/A')
        finally:
            await engine.dispose()

    async def _execute_sync(self, code: str, init_sql: str | None, original_error: Exception) -> pd.DataFrame:
        """Execute query using sync engine as fallback."""
        # Convert async URL to sync URL
        sync_url = self._get_sync_url(self.url)
        engine = create_engine(sync_url, echo=False)
        try:
            with engine.connect() as conn:
                conn = conn.execution_options(readonly=True)
                if init_sql:
                    conn.execute(text(init_sql))
                    conn.commit()
                result = conn.execute(text(code))
                data = result.fetchall()
                logger.debug(f"Sync query executed successfully: {code[:100]}...")
                return pd.DataFrame(data)  # .fillna('N/A')
        except Exception as sync_error:
            logger.error(f"Both async and sync failed. Async: {original_error}, Sync: {sync_error}")
            raise DatabaseError(f"Query execution failed: {sync_error}") from sync_error
        finally:
            engine.dispose()

    def _get_sync_url(self, url: URL) -> URL:
        """Convert async URL to sync URL for fallback."""
        driver_mapping = {
            "postgresql+asyncpg": "postgresql+psycopg2",
            "mysql+aiomysql": "mysql+pymysql",
            "sqlite+aiosqlite": "sqlite",
            "mssql+pyodbc": "mssql+pyodbc",  # SQL Server uses the same driver for sync/async
        }

        if url.drivername in driver_mapping:
            return url.set(drivername=driver_mapping[url.drivername])
        else:
            # For other drivers, just return the original URL
            return url

    def _is_greenlet_error(self, error: Exception) -> bool:
        """Check if error is related to greenlet/async configuration."""
        error_str = str(error).lower()
        return (
            (MissingGreenlet is not None and isinstance(error, MissingGreenlet))
            or "greenlet" in error_str
            or "greenlet_spawn" in error_str
            or "await_only" in error_str
        )

    def _is_asyncpg_auth_error(self, error: Exception) -> bool:
        """Check if error is related to asyncpg authentication issues."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        return (
            "internalclienterror" in error_type.lower()
            or "authentication" in error_str
            or "scram" in error_str
            or "'nonetype' object has no attribute 'group'" in error_str
        )


class Database(BaseModel, ABC):
    """Abstract base class for all databases."""

    url: URL = Field(description="URL of the database")
    model_config = ConfigDict(ignored_types=(immutabledict,), arbitrary_types_allowed=True, frozen=True)

    @field_validator("url", mode="before")
    def validate_url(cls, v: Any) -> URL:
        if isinstance(v, str):
            v = make_url(v)

        return v  # type: ignore[no-any-return]

    @abstractmethod
    async def test_connection(self) -> ConnectionResult:
        """Test the connection to the database."""
        raise NotImplementedError("Subclasses must implement test_connection")

    @abstractmethod
    async def get_tables(self) -> list[str]:
        """Get the tables of the data source."""
        raise NotImplementedError("Subclasses must implement get_tables")

    @abstractmethod
    async def inspect_table(self, table_path: str) -> Any:
        """Inspect the structure of a table at the given path."""
        raise NotImplementedError("Subclasses must implement inspect_table")

    @abstractmethod
    async def sample_table(self, table_path: str, n: int = 5) -> Any:
        """Sample data from the specified table."""
        raise NotImplementedError("Subclasses must implement sample_table")

    @abstractmethod
    async def query(self, code: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a DataFrame."""
        raise NotImplementedError("Subclasses must implement query")

    async def search_tables(self, pattern: str, mode: SearchMode = SearchMode.REGEX, limit: int = 10) -> list[str]:
        """Search for table names using different algorithms."""
        table_names = await self.get_tables()
        if not table_names:
            return []

        try:
            return search_items(table_names, pattern, mode, limit)
        except re.error as e:
            raise DatabaseError(f"Invalid regex pattern '{pattern}': {e}")
        except Exception as e:
            logger.error(f"Table search failed: {e}")
            raise DatabaseError(f"Table search failed: {e}") from e
