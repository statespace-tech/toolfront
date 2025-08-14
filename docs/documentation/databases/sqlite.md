# SQLite

## Installation

```bash
pip install "toolfront[sqlite]"
```

## Connection URL

Connect to SQLite by passing a connection URL to the `Database` constructor:

=== "In-Memory Database"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="sqlite://")

    revenue = db.ask("What's our total revenue this month?")
    ```

=== "File-based Database"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="sqlite://{relative/path/to/mydb.sqlite}")

    revenue = db.ask("What's our total revenue this month?")
    ```

## Connection Parameters

Alternatively, connect using the `Database.from_sqlite()` method with parameters:

```python linenums="1"
from toolfront import Database

# File-based database
db = Database.from_sqlite(database="/path/to/mydb.sqlite")

# In-memory database
db = Database.from_sqlite()

revenue = db.ask("What's our total revenue this month?")
```

::: toolfront.Database.from_sqlite
    options:
      show_signature: false
      show_source: false
      show_root_heading: false
      show_root_toc_entry: false