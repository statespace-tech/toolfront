# Trino

## Installation

```bash
pip install "toolfront[trino]"
```

## Connection URL

Connect to Trino by passing a connection URL to the `Database` constructor:

```python linenums="1" hl_lines="3"
from toolfront import Database

db = Database(url="trino://{user}:{password}@{host}:{port}/{catalog}/{schema}")

revenue = db.ask("What's our total revenue this month?")
```

## Connection Parameters

Alternatively, connect using the `Database.from_trino()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_trino(
    user="user",
    password="pass",
    host="localhost",
    port=8080,
    database="sales",
    schema="public"
)

revenue = db.ask("What's our total revenue this month?")
```