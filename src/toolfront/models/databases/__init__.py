from enum import Enum


class DatabaseType(str, Enum):
    BIGQUERY = "bigquery"
    DATABRICKS = "databricks"
    DUCKDB = "duckdb"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SNOWFLAKE = "snowflake"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"


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

__all__ = ["DatabaseType"]
