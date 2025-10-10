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
@click.argument("db", type=click.STRING, required=True)
@click.pass_context
def database(ctx, db):
    """Database commands for ToolFront CLI."""
    ctx.ensure_object(dict)
    ctx.obj["db"] = db


@database.command()
@click.pass_context
def list_tables(ctx) -> None:
    """List all tables available in the database.

    Notes:
      - Use this to discover what tables exist in the database
      - For multi-database systems, tables are shown as: catalog.database.table

    Example:
      toolfront database $POSTGRES_URL list-tables
    """
    db = ctx.obj["db"]
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
@click.argument("path", type=click.STRING, required=True)
@click.pass_context
def inspect_table(ctx, path) -> None:
    """Inspect table schema and view sample data.

    Arguments:
      PATH  Table path (format: [catalog.][database.]table)

    Notes:
      - ALWAYS inspect tables before querying to understand their structure
      - Shows column names, data types, nullable constraints, and sample values
      - Use this to discover what data is available in each table

    Example:
      toolfront database $POSTGRES_URL inspect-table mydb.mytable
    """
    db = ctx.obj["db"]

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
@click.argument("sql", type=click.STRING, required=True)
@click.pass_context
def query(ctx, sql) -> None:
    """Execute read-only SQL queries against the database.

    Arguments:
      SQL  SQL query to execute (must be read-only)

    Notes:
      - ONLY query tables you've inspected or discovered via list-tables
      - Always quote identifiers (table/column names) to avoid errors
      - Use exact table and column names from inspect-table output
      - Query is restricted to read-only operations (SELECT, WITH, etc.)
      - If query fails, inspect the table schema and retry with corrections

    Example:
      toolfront database $POSTGRES_URL query "SELECT * FROM mytable"
    """
    db = ctx.obj["db"]

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
