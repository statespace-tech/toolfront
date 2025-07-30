import logging
import re
import warnings
from abc import ABC
from contextlib import closing
from typing import Any, get_args, get_origin
from urllib.parse import urlparse

import ibis
import pandas as pd
from ibis import BaseBackend
from pydantic import BaseModel, Field, PrivateAttr, computed_field, field_serializer, model_validator

from toolfront.models.base import DataSource
from toolfront.utils import sanitize_url, serialize_response

logger = logging.getLogger("toolfront")


class Table(BaseModel):
    path: str = Field(
        ...,
        description="Full table path in dot notation e.g. 'schema.table' or 'database.schema.table'.",
    )


class Query(BaseModel):
    code: str = Field(..., description="SQL query string to execute. Must match the SQL dialect of the database.")

    def is_read_only_query(self) -> bool:
        """Check if SQL contains only read operations"""
        # Define write operations that make a query non-read-only
        write_operations = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "CREATE",
            "ALTER",
            "TRUNCATE",
            "REPLACE",
            "MERGE",
            "UPSERT",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
            "CALL",
        ]

        # Create regex pattern that matches any write operation as a complete word
        pattern = r"\b(?:" + "|".join(write_operations) + r")\b"

        # Return True if NO write operations are found (case insensitive)
        return not bool(re.search(pattern, self.code, re.IGNORECASE))


class Database(DataSource, ABC):
    """Abstract base class for all databases.

    Parameters
    ----------
    url : str
        Database URL for connection.
    match_schema : str, optional
        Regex pattern to filter schemas/databases. Passed to list_databases' like parameter.
    match_tables : str, optional
        Regex pattern to filter table names. Passed to list_tables' like parameter.

    Attributes
    ----------
    _connection : BaseBackend or None
        Ibis backend connection to the database.
    _connection_kwargs : dict[str, Any]
        Additional keyword arguments for database connection.
    """

    url: str = Field(description="Database URL.")

    match_schema: str | None = Field(
        default=None,
        description="Regex pattern to filter schemas/databases. Passed to list_databases' like parameter.",
        exclude=True,
    )

    match_tables: str | None = Field(
        default=None,
        description="Regex pattern to filter table names. Passed to list_tables' like parameter.",
        exclude=True,
    )

    _tables: list[str] = PrivateAttr(default_factory=list)
    _connection: BaseBackend | None = PrivateAttr(default=None)
    _connection_kwargs: dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(
        self, url: str, match_schema: str | None = None, match_tables: str | None = None, **kwargs: Any
    ) -> None:
        self._connection_kwargs = kwargs
        super().__init__(url=url, match_schema=match_schema, match_tables=match_tables)

    def __getitem__(self, name: str) -> "ibis.Table":
        parts = name.split(".")
        if not 1 <= len(parts) <= 3:
            raise ValueError(f"Invalid table name: {name}")
        return self._connection.table(parts[-1], database=tuple(parts[:-1]) if len(parts) > 1 else None)

    def __repr__(self) -> str:
        dump = self.model_dump(exclude={"tables"})
        args = ", ".join(f"{k}={repr(v)}" for k, v in dump.items())
        return f"{self.__class__.__name__}({args})"

    @property
    def database_type(self) -> str:
        """Get the database type from the URL scheme."""
        parsed = urlparse(self.url)
        scheme = parsed.scheme.lower()

        # Handle some common aliases
        scheme_mapping = {
            "postgres": "postgresql",
            "mssql": "sqlserver",
        }

        return scheme_mapping.get(scheme, scheme)

    @model_validator(mode="after")
    def model_validator(self) -> "Database":
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Unable to create Ibis UDFs", UserWarning)
            self._connection = ibis.connect(self.url, **self._connection_kwargs)

        # Validate regex patterns
        if self.match_schema:
            if not isinstance(self.match_schema, str):
                raise ValueError(f"match_schema must be a string, got {type(self.match_schema)}")
            try:
                re.compile(self.match_schema)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern for match_schema: {self.match_schema} - {str(e)}")

        if self.match_tables:
            if not isinstance(self.match_tables, str):
                raise ValueError(f"match_tables must be a string, got {type(self.match_tables)}")
            try:
                re.compile(self.match_tables)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern for match_tables: {self.match_tables} - {str(e)}")

        try:
            catalog = getattr(self._connection, "current_catalog", None)
            if catalog:
                databases = self._connection.list_databases(catalog=catalog, like=self.match_schema)
                all_tables = []
                for db in databases:
                    tables = self._connection.list_tables(like=self.match_tables, database=(catalog, db))
                    prefix = f"{catalog}." if catalog else ""
                    all_tables.extend([f"{prefix}{db}.{table}" for table in tables])
            else:
                all_tables = self._connection.list_tables(like=self.match_tables)
        except Exception as e:
            logger.error(f"Failed to discover tables automatically: {e}")
            raise RuntimeError(f"Could not list tables from database: {str(e)}") from e

        if not len(all_tables):
            logger.warning("No tables found in the database - this may be expected for empty databases")

        self._tables = all_tables

        return self

    @field_serializer("url")
    def serialize_url(self, value: str) -> str:
        """Serialize URL field by sanitizing sensitive information.

        Parameters
        ----------
        value : str
            Original database URL.

        Returns
        -------
        str
            Sanitized URL with sensitive information removed.
        """
        return sanitize_url(value)

    @computed_field
    @property
    def tables(self) -> list[str]:
        return self._tables

    def tools(self) -> list[callable]:
        """Return list of available tool methods.

        Returns
        -------
        list[callable]
            List containing inspect_table and query methods.
        """
        return [self.inspect_table, self.query]

    async def inspect_table(
        self,
        table: Table = Field(..., description="Database table to inspect."),
    ) -> dict[str, Any]:
        """Inspect the schema of database table and get sample data.

        1. Use this tool to understand table structure like column names, data types, and constraints
        2. Inspecting tables helps understand the structure of the data
        3. ALWAYS inspect unfamiliar tables first to learn their columns and data types before querying
        """
        try:
            logger.debug(f"Inspecting table: {self.url} {table.path}")
            table = self[table.path]
            return {
                "schema": serialize_response(table.info()[["name", "type", "nullable"]].to_pandas()),
                "samples": serialize_response(table.head(5).to_pandas()),
            }
        except Exception as e:
            logger.error(f"Failed to inspect table: {e}", exc_info=True)
            raise RuntimeError(f"Failed to inspect table {table.path} in {self.url} - {str(e)}") from e

    async def query(
        self,
        query: Query = Field(..., description="Read-only SQL query to execute."),
    ) -> dict[str, Any]:
        """
        This tool allows you to run read-only SQL queries against a database.

        ALWAYS ENCLOSE IDENTIFIERS (TABLE NAMES, COLUMN NAMES) IN QUOTES TO PRESERVE CASE SENSITIVITY AND AVOID RESERVED WORD CONFLICTS AND SYNTAX ERRORS.

        1. ONLY write read-only queries for tables that have been explicitly discovered or referenced.
        2. Before writing queries, make sure you understand the schema of the tables you are querying.
        3. ALWAYS use the correct dialect for the database.
        4. NEVER use aliases in queries unless strictly necessary.
        5. When a query fails or returns unexpected results, try to diagnose the issue and then retry.
        """
        logger.debug(f"Querying database: {self.url} {query.code}")
        if not query.is_read_only_query():
            raise ValueError("Only read-only queries are allowed")

        if not hasattr(self._connection, "raw_sql"):
            raise ValueError("Database does not support raw sql queries")

        with closing(self._connection.raw_sql(query.code)) as cursor:
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(cursor.fetchall(), columns=columns)
            return serialize_response(df)

    def _preprocess(self, var_type: Any) -> Any:
        if var_type == pd.DataFrame:
            return Query

        origin = get_origin(var_type)
        if origin is not None:
            args = get_args(var_type)
            if pd.DataFrame in args:
                return Query | None if type(None) in args else Query

        return var_type

    def query_raw(self, query: Query) -> pd.DataFrame:
        """Execute query and return raw DataFrame without truncation."""
        if not query.is_read_only_query():
            raise ValueError("Only read-only queries are allowed")

        if not hasattr(self._connection, "raw_sql"):
            raise ValueError("Database does not support raw sql queries")

        with closing(self._connection.raw_sql(query.code)) as cursor:
            columns = [col[0] for col in cursor.description]
            return pd.DataFrame(cursor.fetchall(), columns=columns)

    def _postprocess(self, result: Any) -> Any:
        if isinstance(result, Query):
            return self.query_raw(result)
        return result
