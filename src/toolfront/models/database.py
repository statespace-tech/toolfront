import logging
import re
import warnings
from abc import ABC
from pathlib import Path
from typing import Any, Generic, TypeVar
from urllib.parse import urlparse

import ibis
import pandas as pd
import yaml
from ibis import BaseBackend
from pydantic import BaseModel, Field, PrivateAttr, computed_field, field_serializer, model_validator
from pydantic_ai import ModelRetry
from sqlglot.optimizer import optimize

from toolfront.models.base import DataSource
from toolfront.utils import sanitize_url

logger = logging.getLogger("toolfront")

T = TypeVar("T", bound=BaseModel)


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

    def optimized_code(self, dialect: str) -> str:
        return optimize(self.code, dialect=dialect).sql(dialect=dialect)


class Database(DataSource, ABC):
    """Natural language interface for databases.

    Supports 15+ database types including PostgreSQL, MySQL, SQLite, Snowflake, BigQuery.

    Parameters
    ----------
    url : str
        Database connection URL (e.g., 'postgresql://user:pass@host/db')
    match_schema : str, optional
        Regex pattern to filter schemas. Mutually exclusive with match_tables.
    match_tables : str, optional
        Regex pattern to filter tables. Mutually exclusive with match_schema.
    """

    model_config = {"arbitrary_types_allowed": True}

    url: str = Field(description="Database URL.")
    connection: BaseBackend = Field(description="Ibis database connection.", exclude=True)

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

    def __init__(
        self,
        url: str,
        connection: BaseBackend | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> None:
        # Create connection if not provided
        if connection is None:
            if "://" not in url:
                url = f"{url}://"

            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", "Unable to create Ibis UDFs", UserWarning)
                connection = ibis.connect(url, **kwargs)

        super().__init__(url=url, connection=connection, match_schema=match_schema, match_tables=match_tables)

    def __getitem__(self, name: str) -> "ibis.Table":
        parts = name.split(".")
        if not 1 <= len(parts) <= 3:
            raise ValueError(f"Invalid table name: {name}")
        return self.connection.table(parts[-1], database=tuple(parts[:-1]) if len(parts) > 1 else None)

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
    def validate_and_discover_tables(self) -> "Database":
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
            catalog = getattr(self.connection, "current_catalog", None)
            if catalog:
                databases = self.connection.list_databases(catalog=catalog, like=self.match_schema)
                all_tables = []
                for db in databases:
                    tables = self.connection.list_tables(like=self.match_tables, database=(catalog, db))
                    prefix = f"{catalog}." if catalog else ""
                    all_tables.extend([f"{prefix}{db}.{table}" for table in tables])
            else:
                all_tables = self.connection.list_tables(like=self.match_tables)
        except Exception as e:
            logger.error(f"Failed to discover tables automatically: {e}")
            raise RuntimeError(f"Could not list tables from database: {str(e)}") from e

        if not all_tables:
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

    @field_serializer("connection")
    def serialize_connection(self, value: BaseBackend) -> str:
        """Serialize connection as a string representation."""
        return f"<{type(value).__name__} connection>"

    @computed_field
    @property
    def tables(self) -> list[str]:
        return self._tables

    @classmethod
    def from_druid(
        cls,
        host: str,
        port: int,
        path: str | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        host : str
            Hostname or IP address of the Druid broker node.
        port : int
            Port number for the Druid broker node.
        path : str, optional
            Path to the Druid endpoint (if needed).
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            "host": host,
            "port": port,
            **kwargs,
        }

        if path is not None:
            connection_kwargs["path"] = path

        return cls(
            url="druid://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_duckdb(
        cls,
        database: str | None = ":memory:",
        read_only: bool = False,
        extensions: list[str] | None = None,
        config: dict[str, Any] | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        database : str, optional
            Path to a duckdb database.
            Default is ':memory:'.
        read_only : bool, optional
            Whether the database is read-only.
            Default is False.
        extensions : list[str], optional
            A list of duckdb extensions to install/load upon connection.
        config : dict[str, Any], optional
            DuckDB configuration parameters. See the DuckDB configuration documentation for possible configuration values.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            "database": database,
            "read_only": read_only,
            **kwargs,
        }

        if extensions is not None:
            connection_kwargs["extensions"] = extensions
        if config is not None:
            connection_kwargs["config"] = config

        return cls(
            url="duckdb://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_flink(
        cls,
        table_env,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        table_env : TableEnvironment
            PyFlink TableEnvironment instance.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            "table_env": table_env,
            **kwargs,
        }

        return cls(
            url="flink://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_mssql(
        cls,
        host: str = "localhost",
        user: str | None = None,
        password: str | None = None,
        port: int = 1433,
        database: str | None = None,
        driver: str | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        host : str, optional
            Address of MSSQL server to connect to.
            Default is 'localhost'.
        user : str, optional
            Username. Leave blank to use Integrated Authentication.
        password : str, optional
            Password. Leave blank to use Integrated Authentication.
        port : int, optional
            Port of MSSQL server to connect to.
            Default is 1433.
        database : str, optional
            The MSSQL database to connect to.
        driver : str, optional
            ODBC Driver to use. On Mac and Linux this is usually 'FreeTDS'. On Windows, it is usually one of: - ODBC Driver 11 for SQL Server - ODBC Driver 13 for SQL Server (for both 13 and 13.1) - ODBC Driver 17 for SQL Server - ODBC Driver 18 for SQL Server See https://learn.microsoft.com/en-us/sql/connect/odbc/windows/system-requirements-installation-and-driver-files
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional keyword arguments to pass to PyODBC.
        """
        connection_kwargs = {
            "host": host,
            "port": port,
            **kwargs,
        }

        if user is not None:
            connection_kwargs["user"] = user
        if password is not None:
            connection_kwargs["password"] = password
        if database is not None:
            connection_kwargs["database"] = database
        if driver is not None:
            connection_kwargs["driver"] = driver

        return cls(
            url="mssql://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_bigquery(
        cls,
        project_id: str | None = None,
        dataset_id: str = "",
        credentials=None,
        application_name: str | None = None,
        auth_local_webserver: bool = True,
        auth_external_data: bool = False,
        auth_cache: str = "default",
        partition_column: str | None = "PARTITIONTIME",
        client=None,
        storage_client=None,
        location: str | None = None,
        generate_job_id_prefix=None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        project_id : str, optional
            A BigQuery project id.
        dataset_id : str, optional
            A dataset id that lives inside of the project indicated by project_id.
            Default is ''.
        credentials : google.auth.credentials.Credentials, optional
            Optional credentials.
        application_name : str, optional
            A string identifying your application to Google API endpoints.
        auth_local_webserver : bool, optional
            Use a local webserver for the user authentication. Binds a webserver to an open port on localhost between 8080 and 8089, inclusive, to receive authentication token. If not set, defaults to False, which requests a token via the console.
            Default is True.
        auth_external_data : bool, optional
            Authenticate using additional scopes required to query external data sources, such as Google Sheets, files in Google Cloud Storage, or files in Google Drive. If not set, defaults to False, which requests the default BigQuery scopes.
            Default is False.
        auth_cache : str, optional
            Selects the behavior of the credentials cache. 'default' - Reads credentials from disk if available, otherwise authenticates and caches credentials to disk. 'reauth' - Authenticates and caches credentials to disk. 'none' - Authenticates and does not cache credentials.
            Default is 'default'.
        partition_column : str, optional
            Identifier to use instead of default _PARTITIONTIME partition column.
            Default is 'PARTITIONTIME'.
        client : bq.Client, optional
            A Client from the google.cloud.bigquery package. If not set, one is created using the project_id and credentials.
        storage_client : bqstorage.BigQueryReadClient, optional
            A BigQueryReadClient from the google.cloud.bigquery_storage_v1 package. If not set, one is created using the project_id and credentials.
        location : str, optional
            Default location for BigQuery objects.
        generate_job_id_prefix : Callable[[], str | None], optional
            Optional callable that generates a bigquery job ID prefix. If specified, for any query job, jobs will always be created rather than optionally created by BigQuery's Client.query_and_wait.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.


        """
        connection_kwargs = {
            "dataset_id": dataset_id,
            "auth_local_webserver": auth_local_webserver,
            "auth_external_data": auth_external_data,
            "auth_cache": auth_cache,
            "partition_column": partition_column,
            **kwargs,
        }

        if project_id is not None:
            connection_kwargs["project_id"] = project_id
        if credentials is not None:
            connection_kwargs["credentials"] = credentials
        if application_name is not None:
            connection_kwargs["application_name"] = application_name
        if client is not None:
            connection_kwargs["client"] = client
        if storage_client is not None:
            connection_kwargs["storage_client"] = storage_client
        if location is not None:
            connection_kwargs["location"] = location
        if generate_job_id_prefix is not None:
            connection_kwargs["generate_job_id_prefix"] = generate_job_id_prefix

        return cls(
            url="bigquery://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_clickhouse(
        cls,
        host: str = "localhost",
        port: int | None = None,
        database: str = "default",
        user: str = "default",
        password: str = "",
        client_name: str = "ibis",
        secure: bool | None = None,
        compression: str | bool = True,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        host : str, optional
            Host name of the ClickHouse server.
            Default is 'localhost'.
        port : int, optional
            ClickHouse HTTP server's port. If not passed, the value depends on whether secure is True or False.
        database : str, optional
            Default database when executing queries.
            Default is 'default'.
        user : str, optional
            User to authenticate with.
            Default is 'default'.
        password : str, optional
            Password to authenticate with.
            Default is ''.
        client_name : str, optional
            Name of client that will appear in ClickHouse server logs.
            Default is 'ibis'.
        secure : bool, optional
            Whether or not to use an authenticated endpoint.
        compression : str or bool, optional
            The kind of compression to use for requests. See ClickHouse Python Compression Docs for more information.
            Default is True.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Client specific keyword arguments.
        """
        connection_kwargs = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "client_name": client_name,
            "compression": compression,
            **kwargs,
        }

        if port is not None:
            connection_kwargs["port"] = port
        if secure is not None:
            connection_kwargs["secure"] = secure

        return cls(
            url="clickhouse://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_databricks(
        cls,
        server_hostname: str,
        http_path: str,
        access_token: str,
        catalog: str | None = None,
        schema: str | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        server_hostname : str
            Databricks workspace hostname.
        http_path : str
            HTTP path to the Databricks warehouse.
        access_token : str
            Personal access token for authentication.
        catalog : str, optional
            Name of the catalog to use.
        schema : str, optional
            Name of the schema to use.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            "server_hostname": server_hostname,
            "http_path": http_path,
            "access_token": access_token,
            **kwargs,
        }

        if catalog is not None:
            connection_kwargs["catalog"] = catalog
        if schema is not None:
            connection_kwargs["schema"] = schema

        return cls(
            url="databricks://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_mysql(
        cls,
        host: str = "localhost",
        user: str | None = None,
        password: str | None = None,
        port: int = 3306,
        database: str | None = None,
        autocommit: bool = True,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        host : str, optional
            Hostname.
            Default is 'localhost'.
        user : str, optional
            Username.
        password : str, optional
            Password.
        port : int, optional
            Port.
            Default is 3306.
        database : str, optional
            Database name.
        autocommit : bool, optional
            Autocommit mode.
            Default is True.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional keyword arguments passed to MySQLdb.connect.
        """
        connection_kwargs = {
            "host": host,
            "port": port,
            "autocommit": autocommit,
            **kwargs,
        }

        if user is not None:
            connection_kwargs["user"] = user
        if password is not None:
            connection_kwargs["password"] = password
        if database is not None:
            connection_kwargs["database"] = database

        return cls(
            url="mysql://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_oracle(
        cls,
        user: str,
        password: str,
        host: str = "localhost",
        port: int = 1521,
        database: str | None = None,
        sid: str | None = None,
        service_name: str | None = None,
        dsn: str | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        user : str
            Username.
        password : str
            Password.
        host : str, optional
            Hostname.
            Default is 'localhost'.
        port : int, optional
            Port.
            Default is 1521.
        database : str, optional
            Used as an Oracle service name if provided.
        sid : str, optional
            Unique name of an Oracle Instance, used to construct a DSN if provided.
        service_name : str, optional
            Oracle service name, used to construct a DSN if provided. Only one of database and service_name should be provided.
        dsn : str, optional
            An Oracle Data Source Name. If provided, overrides all other connection arguments except username and password.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            **kwargs,
        }

        if database is not None:
            connection_kwargs["database"] = database
        if sid is not None:
            connection_kwargs["sid"] = sid
        if service_name is not None:
            connection_kwargs["service_name"] = service_name
        if dsn is not None:
            connection_kwargs["dsn"] = dsn

        return cls(
            url="oracle://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_postgresql(
        cls,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
        port: int = 5432,
        database: str | None = None,
        schema: str | None = None,
        autocommit: bool = True,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        host : str, optional
            Hostname.
        user : str, optional
            Username.
        password : str, optional
            Password.
        port : int, optional
            Port number.
            Default is 5432.
        database : str, optional
            Database to connect to.
        schema : str, optional
            PostgreSQL schema to use. If None, use the default search_path.
        autocommit : bool, optional
            Whether or not to autocommit.
            Default is True.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional keyword arguments to pass to the backend client connection.
        """
        connection_kwargs = {
            "port": port,
            "autocommit": autocommit,
            **kwargs,
        }

        if host is not None:
            connection_kwargs["host"] = host
        if user is not None:
            connection_kwargs["user"] = user
        if password is not None:
            connection_kwargs["password"] = password
        if database is not None:
            connection_kwargs["database"] = database
        if schema is not None:
            connection_kwargs["schema"] = schema

        return cls(
            url="postgres://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_pyspark(
        cls,
        session=None,
        mode: str = "batch",
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        session : SparkSession, optional
            A SparkSession instance.
        mode : str, optional
            Can be either "batch" or "streaming". If "batch", every source, sink, and query executed within this connection will be interpreted as a batch workload. If "streaming", every source, sink, and query executed within this connection will be interpreted as a streaming workload.
            Default is 'batch'.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional keyword arguments used to configure the SparkSession.
        """
        connection_kwargs = {
            "mode": mode,
            **kwargs,
        }

        if session is not None:
            connection_kwargs["session"] = session

        return cls(
            url="pyspark://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_risingwave(
        cls,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
        port: int = 5432,
        database: str | None = None,
        schema: str | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        host : str, optional
            Hostname.
        user : str, optional
            Username.
        password : str, optional
            Password.
        port : int, optional
            Port number.
            Default is 5432.
        database : str, optional
            Database to connect to.
        schema : str, optional
            RisingWave schema to use. If None, use the default search_path.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            "port": port,
            **kwargs,
        }

        if host is not None:
            connection_kwargs["host"] = host
        if user is not None:
            connection_kwargs["user"] = user
        if password is not None:
            connection_kwargs["password"] = password
        if database is not None:
            connection_kwargs["database"] = database
        if schema is not None:
            connection_kwargs["schema"] = schema

        return cls(
            url="risingwave://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_sqlite(
        cls,
        database: str | None = None,
        type_map: dict[str, str] | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        database : str, optional
            File path to the SQLite database file. If None, creates an in-memory transient database and you can use attach() to add more files.
        type_map : dict[str, str], optional
            An optional mapping from a string name of a SQLite "type" to the corresponding Ibis DataType that it represents. This can be used to override schema inference for a given SQLite database.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            **kwargs,
        }

        if database is not None:
            connection_kwargs["database"] = database
        if type_map is not None:
            connection_kwargs["type_map"] = type_map

        return cls(
            url="sqlite://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_trino(
        cls,
        user: str = "user",
        password: str | None = None,
        host: str = "localhost",
        port: int = 8080,
        database: str | None = None,
        schema: str | None = None,
        source: str | None = None,
        timezone: str = "UTC",
        auth: str | None = None,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        user : str, optional
            Username to connect with.
            Default is 'user'.
        password : str, optional
            Password to connect with. Mutually exclusive with auth.
        host : str, optional
            Hostname of the Trino server.
            Default is 'localhost'.
        port : int, optional
            Port of the Trino server.
            Default is 8080.
        database : str, optional
            Catalog to use on the Trino server.
        schema : str, optional
            Schema to use on the Trino server.
        source : str, optional
            Application name passed to Trino.
        timezone : str, optional
            Timezone to use for the connection.
            Default is 'UTC'.
        auth : str, optional
            Authentication method to use for the connection. Mutually exclusive with password.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional keyword arguments passed directly to the trino.dbapi.connect API.
        """
        connection_kwargs = {
            "user": user,
            "host": host,
            "port": port,
            "timezone": timezone,
            **kwargs,
        }

        if password is not None:
            connection_kwargs["password"] = password
        if database is not None:
            connection_kwargs["database"] = database
        if schema is not None:
            connection_kwargs["schema"] = schema
        if source is not None:
            connection_kwargs["source"] = source
        if auth is not None:
            connection_kwargs["auth"] = auth

        return cls(
            url="trino://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    @classmethod
    def from_snowflake(
        cls,
        user: str,
        account: str,
        database: str,
        password: str | None = None,
        authenticator: str | None = None,
        create_object_udfs: bool = True,
        match_schema: str | None = None,
        match_tables: str | None = None,
        **kwargs: Any,
    ) -> "Database":
        """
        Parameters
        ----------
        user : str
            Username
        account : str
            A Snowflake organization ID and a Snowflake user ID, separated by a hyphen.
            Note that a Snowflake user ID is a separate identifier from a username.
            See https://docs.snowflake.com/en/user-guide/admin-account-identifier for details
        database : str
            A Snowflake database and a Snowflake schema, separated by a /.
            See https://docs.snowflake.com/en/sql-reference/ddl-database for details
        password : str, optional
            Password. If empty or None then authenticator must be passed.
        authenticator : str, optional
            String indicating authentication method.
            See https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example#connecting-with-oauth for details.
            Note that the authentication flow will not take place until a database connection is made.
            This means that connection can succeed, while subsequent API calls fail if the authentication fails for any reason.
        create_object_udfs : bool, optional
            Enable object UDF extensions defined on the first connection to the database.
            Default is True.
        match_schema : str, optional
            Regex pattern to filter schemas. Mutually exclusive with match_tables.
        match_tables : str, optional
            Regex pattern to filter tables. Mutually exclusive with match_schema.
        **kwargs : Any
            Additional arguments passed to the DBAPI connection call.
        """
        connection_kwargs = {
            "user": user,
            "account": account,
            "database": database,
            "create_object_udfs": create_object_udfs,
            **kwargs,
        }

        if password is not None:
            connection_kwargs["password"] = password

        if authenticator is not None:
            connection_kwargs["authenticator"] = authenticator

        return cls(
            url="snowflake://",
            match_schema=match_schema,
            match_tables=match_tables,
            **connection_kwargs,
        )

    def tools(self) -> list[callable]:
        """Available tool methods for database operations.

        Returns
        -------
        list[callable]
            Methods for table inspection and query execution.
        """
        return [self.inspect_table, self.query]

    async def inspect_table(
        self,
        table: Table = Field(..., description="Database table to inspect."),
    ) -> dict[str, Any]:
        """Inspect the schema of database table and get sample data.

        Instructions:
        1. Use this tool to understand table structure like column names, data types, and constraints
        2. Inspecting tables helps understand the structure of the data
        3. ALWAYS inspect unfamiliar tables first to learn their columns and data types before querying
        """
        try:
            logger.debug(f"Inspecting table: {self.url} {table.path}")
            inspected_table = self[table.path]
            return {
                "schema": inspected_table.info()[["name", "type", "nullable"]].to_pandas(),
                "samples": inspected_table.head(5).to_pandas(),
            }
        except Exception as e:
            logger.error(f"Failed to inspect table: {e}", exc_info=True)
            raise ModelRetry(f"Failed to inspect table: {str(e)}") from e

    async def query(
        self,
        query: Query = Field(..., description="Read-only SQL query to execute."),
    ) -> dict[str, Any]:
        """Run read-only SQL queries against a database.

        ALWAYS ENCLOSE ALL IDENTIFIERS (TABLE NAMES, COLUMN NAMES) IN QUOTES TO PRESERVE CASE SENSITIVITY AND AVOID RESERVED WORD CONFLICTS AND SYNTAX ERRORS.

        Instructions:
        1. ONLY write read-only queries for tables that have been explicitly discovered or referenced
        2. Always use the exact table and column names as they appear in the schema, respecting case sensitivity
        3. Before writing queries, make sure you understand the schema of the tables you are querying.
        4. When a query fails or returns unexpected results, try to diagnose the issue and then retry.
        """
        try:
            logger.debug(f"Querying database: {self.url} {query.code}")
            if not query.is_read_only_query():
                raise ValueError("Only read-only queries are allowed")

            if not hasattr(self.connection, "raw_sql"):
                raise ValueError("Database does not support raw sql queries")

            result = self.connection.sql(query.optimized_code(self.database_type))

            return result.to_pandas()
        except Exception as e:
            logger.error(f"Failed to query database: {e}", exc_info=True)
            raise ModelRetry(f"Failed to query database: {str(e)}") from e

    def _query_sync(self, query: Query) -> pd.DataFrame:
        """Synchronous version of query method for internal use."""
        try:
            logger.debug(f"Querying database: {self.url} {query.code}")
            if not query.is_read_only_query():
                raise ValueError("Only read-only queries are allowed")

            return self.connection.sql(query.optimized_code(self.database_type)).to_pandas()
        except Exception as e:
            logger.error(f"Failed to query database: {e}", exc_info=True)
            raise RuntimeError(f"Failed to query database:{str(e)}") from e

    @property
    def Table(self) -> type:  # noqa: N802
        db = self

        class Table(BaseModel, Generic[T]):
            """A table that validates and structures query results according to a Pydantic model."""

            query: Query = Field(..., description="Query to execute.")
            _data: pd.DataFrame = PrivateAttr(default_factory=pd.DataFrame)
            _row_type: type[T] = PrivateAttr()

            def __class_getitem__(cls, item):
                """Capture the generic type parameter and create a new class with _model_type set."""
                # Read the query instructions template
                instructions_path = Path("src/toolfront/instructions/query.txt")
                instructions = instructions_path.read_text()

                # Generate field descriptions from the model as YAML dict
                fields_dict = {}
                for field_name, field_info in item.model_fields.items():
                    field_type = field_info.annotation
                    type_name = field_type.__name__ if hasattr(field_type, "__name__") else str(field_type)
                    fields_dict[field_name] = type_name

                fields_yaml = yaml.dump(fields_dict, default_flow_style=False)

                instructions += "Required fields:\n" + fields_yaml

                class ParameterizedTable(cls):
                    _row_type: type[T] = PrivateAttr(default=item)
                    query: Query = Field(..., description=instructions)

                ParameterizedTable.__name__ = f"Table[{item.__name__}]"
                return ParameterizedTable

            @model_validator(mode="after")
            def validate_query_results(self) -> "Table":
                """Validate datasource and query results."""
                # Validate query is read-only
                if not self.query.is_read_only_query():
                    raise ValueError("Only read-only queries are allowed")

                data = db._query_sync(self.query)

                if self._row_type:
                    self._validate_fields(data.columns)
                    self._data = data[list(self._row_type.model_fields.keys())]
                else:
                    self._data = data
                return self

            def _validate_fields(self, actual_columns: list[str]) -> None:
                """Validate field names match exactly."""
                expected = set(self._row_type.model_fields.keys())
                actual = set(actual_columns)

                if expected != actual:
                    missing = expected - actual
                    extra = actual - expected
                    errors = []
                    if missing:
                        errors.append(f"Missing: {missing}")
                    if extra:
                        errors.append(f"Extra: {extra}")
                    raise ValueError(f"Field mismatch. {', '.join(errors)}")

            def to_dataframe(self) -> pd.DataFrame:
                """Return the underlying DataFrame."""
                return self._data

            def __len__(self) -> int:
                return len(self._data)

            def __iter__(self):
                for _, row in self._data.iterrows():
                    if self._row_type is not None:
                        yield self._row_type(**row.to_dict())
                    else:
                        yield row.to_dict()

        return Table
