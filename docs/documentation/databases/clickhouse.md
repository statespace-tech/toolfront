# ClickHouse

## Installation

```bash
pip install "toolfront[clickhouse]"
```

## Connection URL

Connect to ClickHouse by passing a connection URL to the `Database` constructor:

<div class="tabbed-set" markdown="1">

=== "Basic"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="clickhouse://{user}:{password}@{host}:{port}/{database}")

    revenue = db.ask("What's our total revenue this month?")
    ```

=== "With Secure Connection"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="clickhouse://{user}:{password}@{host}:{port}/{database}?secure=true")

    revenue = db.ask("What's our total revenue this month?")
    ```

=== "With Compression"
    ```python linenums="1" hl_lines="3"
    from toolfront import Database

    db = Database(url="clickhouse://{user}:{password}@{host}:{port}/{database}?compression=lz4")

    revenue = db.ask("What's our total revenue this month?")
    ```

</div>

## Connection Parameters

Alternatively, connect using the `Database.from_clickhouse()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_clickhouse(
    host="localhost",
    port=9000,
    database="sales",
    user="user",
    password="pass",
    secure=False
)

revenue = db.ask("What's our total revenue this month?")