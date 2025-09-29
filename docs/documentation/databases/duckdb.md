# DuckDB

## Installation

```bash
pip install "toolfront[duckdb]"
```

## Connection URL

Connect to DuckDB by passing a connection URL to the `Database` constructor:

=== "In-memory Database"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="duckdb://")

    revenue = db.ask("What's our total revenue this month?")
    ```

=== "File-based Database"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="duckdb://{path/to/database.db}")

    revenue = db.ask("What's our total revenue this month?")
    ```

## Connection Parameters

Alternatively, connect using the `Database.from_duckdb()` method with parameters:

```python linenums="1"
from toolfront import Database

# In-memory database
db = Database.from_duckdb()

# File-based database with extensions
db = Database.from_duckdb(
    database="mydata.duckdb",
    extensions=["httpfs", "parquet"],
    config={"threads": 4}
)

revenue = db.ask("What's our total revenue this month?")
```