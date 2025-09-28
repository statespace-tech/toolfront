import json
import os
import re
import warnings
from urllib.parse import parse_qsl, urlparse

import click
import ibis
from ibis import BaseBackend

NUM_TABLE_SAMPLES = 5
MAX_COLUMN_WIDTH = 1024


def create_connection(db: str) -> BaseBackend:
    """Create database connection using Ibis backend.

    Parameters
    ----------
    db : str
        Database connection string or environment variable name

    Returns
    -------
    BaseBackend
        Connected Ibis backend instance
    """
    db = os.environ.get(db, db)
    kwargs = dict(parse_qsl(urlparse(db).query, keep_blank_values=True))
    kwargs = {k: json.loads(v) for k, v in kwargs.items()}

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "Unable to create Ibis UDFs", UserWarning)
        connection = ibis.connect(db, **kwargs)

    return connection


def is_read_only_query(sql) -> bool:
    """Check if SQL contains only read operations.

    Parameters
    ----------
    sql : str
        SQL query string to analyze

    Returns
    -------
    bool
        True if query is read-only, False if it contains write operations
    """
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
    return not bool(re.search(pattern, sql, re.IGNORECASE))


@click.group()
def database():
    """Database commands for ToolFront CLI."""
    pass


@database.command()
@click.argument("db", type=click.STRING, required=True)
def list_tables(db) -> None:
    """List available tables in the database.

    Usage: `database list-tables DB`

    Parameters
    ----------
    db : str
        Database connection string or environment variable name

    Example
    -------
    ```bash
    uvx toolfront database list-tables postgres://user:password@localhost:5432/mydb
    ```
    """
    click.echo(os.environ.get(db, db))
    connection = create_connection(db)

    catalog = getattr(connection, "current_catalog", None)
    dataset = getattr(connection, "dataset", None)

    if catalog and dataset:
        tables = connection.list_tables(database=(catalog, dataset))
        click.echo([f"{catalog}.{dataset}.{table}" for table in tables])
    elif catalog:
        all_tables = []
        databases = connection.list_databases(catalog=catalog) if hasattr(connection, "list_databases") else []  # type: ignore

        for db in databases:
            try:
                tables = connection.list_tables(database=(catalog, db))
                all_tables.extend([f"{catalog}.{db}.{table}" for table in tables])
            except Exception:
                pass

        click.echo(all_tables)
    else:
        click.echo(connection.list_tables())


@database.command()
@click.argument("db", type=click.STRING, required=True)
@click.argument("path", type=click.STRING, required=True)
def inspect_table(db, path) -> None:
    """Inspect the schema of database table and get sample data.

    Usage: `database inspect-table DB PATH`

    Parameters
    ----------
    db : str
        Database connection string or environment variable name
    path : str
        Table path to inspect

    LLM Instructions
    ----------------
    1. Use this tool to understand table structure like column names, data types, and constraints
    2. Inspecting tables helps understand the structure of the data
    3. ALWAYS inspect unfamiliar tables first to learn their columns and data types before querying

    Example
    -------
    ```bash
    uvx toolfront database inspect-table postgres://user:password@localhost:5432/mydb mydb.mytable
    ```
    """

    parts = path.split(".")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"Invalid table: {path}")

    connection = create_connection(db)

    table = connection.table(parts[-1], database=tuple(parts[:-1]) if len(parts) > 1 else None)
    data = table.info()[["name", "type", "nullable"]].to_pandas()
    table_length = table.count().execute()
    samples = table.sample(NUM_TABLE_SAMPLES / table_length).to_pandas()
    data["samples"] = data["name"].map(lambda c: "; ".join(map(str, samples[c].dropna())))

    for col in data.select_dtypes(include=["object"]).columns:
        data[col] = data[col].apply(
            lambda x: x[:MAX_COLUMN_WIDTH] + "..." if isinstance(x, str) and len(x) > MAX_COLUMN_WIDTH else x
        )

    click.echo(data.to_markdown(index=False))


@database.command()
@click.argument("db", type=click.STRING, required=True)
@click.argument("sql", type=click.STRING, required=True)
def query(db, sql) -> None:
    """Run read-only SQL queries against a database.

    Usage: `database query DB SQL`

    Parameters
    ----------
    db : str
        Database connection string or environment variable name
    sql : str
        SQL query code to execute

    LLM Instructions
    ----------------
    1. Always enclose all identifiers (table names, column names) in quotes to preserve case sensitivity and avoid reserved word conflicts and syntax errors.
    1. ONLY write read-only queries for tables that have been explicitly discovered or referenced
    2. Always use the exact table and column names as they appear in the schema, respecting case sensitivity
    3. Before writing queries, make sure you understand the schema of the tables you are querying
    4. When a query fails or returns unexpected results, try to diagnose the issue and then retry        

    Example
    -------
    ```bash
    uvx toolfront database query postgres://user:password@localhost:5432/mydb "SELECT * FROM mytable"
    ```
    """

    if not is_read_only_query(sql):
        raise click.ClickException("SQL query must be read-only.")
    connection = create_connection(db)

    if hasattr(connection, "sql"):
        data = connection.sql(sql).to_pandas()  # type: ignore
        for col in data.select_dtypes(include=["object"]).columns:
            data[col] = data[col].apply(
                lambda x: x[:MAX_COLUMN_WIDTH] + "..." if isinstance(x, str) and len(x) > MAX_COLUMN_WIDTH else x
            )
        click.echo(data.to_markdown(index=False))
    else:
        raise ValueError("Database does not support raw sql queries")


if __name__ == "__main__":
    database()
