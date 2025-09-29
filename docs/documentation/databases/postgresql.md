# PostgreSQL

## Installation

```bash
pip install "toolfront[postgres]"
```

## Connection URL

Connect to PostgreSQL by passing a connection URL to the `Database` constructor:

=== "All Schemas"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="postgres://{user}:{password}@{host}:{port}/{database}")

    revenue = db.ask("What's our total revenue this month?")
    ```

=== "Specific Schema"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="postgres://{user}:{password}@{host}:{port}/{database}/{schema}")

    revenue = db.ask("What's our total revenue this month?")
    ```

=== "With SSL Enabled"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="postgres://{user}:{password}@{host}:{port}/{database}/{schema}?sslmode=require")

    revenue = db.ask("What's our total revenue this month?")
    ```

## Connection Parameters

Alternatively, connect using the `Database.from_postgresql()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_postgresql(
    host="localhost",
    port=5432,
    database="sales",
    user="user",
    password="pass",
    schema="public"
)

revenue = db.ask("What's our total revenue this month?")
```