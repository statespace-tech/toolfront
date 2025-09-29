# MSSQL

## Installation

```bash
pip install "toolfront[mssql]"
```

## Connection URL

Connect to MSSQL by passing a connection URL to the `Database` constructor:

```python linenums="1" hl_lines="3"
from toolfront import Database

db = Database(url="mssql://{user}:{password}@{host}:{port}")

revenue = db.ask("What's our total revenue this month?")
```

## Connection Parameters

Alternatively, connect using the `Database.from_mssql()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_mssql(
    host="localhost",
    port=1433,
    database="sales",
    user="user",
    password="pass"
)

revenue = db.ask("What's our total revenue this month?")
```