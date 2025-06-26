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


__all__ = ["DatabaseType"]
