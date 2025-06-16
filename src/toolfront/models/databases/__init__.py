from enum import Enum

from .bigquery import BigQuery
from .databricks import Databricks
from .duckdb import DuckDB
from .mysql import MySQL
from .postgresql import PostgreSQL
from .snowflake import Snowflake
from .sqlite import SQLite
from .sqlserver import SQLServer


class DatabaseType(str, Enum):
    BIGQUERY = "bigquery"
    DATABRICKS = "databricks"
    DUCKDB = "duckdb"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SNOWFLAKE = "snowflake"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"


__all__ = [
    "BigQuery",
    "Databricks",
    "DuckDB",
    "MySQL",
    "PostgreSQL",
    "Snowflake",
    "SQLite",
    "SQLServer",
    "DatabaseType",
]
