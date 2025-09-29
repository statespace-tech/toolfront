# Druid

## Installation

```bash
pip install "toolfront[druid]"
```

## Connection URL

Connect to Druid by passing a connection URL to the `Database` constructor:

```python linenums="1" hl_lines="3"
from toolfront import Database

db = Database(url="druid://{host}:{port}/{path}")

revenue = db.ask("What's our total revenue this month?")
```

## Connection Parameters

Alternatively, connect using the `Database.from_druid()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_druid(
    host="localhost",
    port=8082,
    path="druid/v2/sql"
)

revenue = db.ask("What's our total revenue this month?")
```