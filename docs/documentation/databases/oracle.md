# Oracle

## Installation

```bash
pip install "toolfront[oracle]"
```

## Connection URL

Connect to Oracle by passing a connection URL to the `Database` constructor:

```python linenums="1" hl_lines="3"
from toolfront import Database

db = Database(url="oracle://{user}:{password}@{host}:{port}/{database}")

revenue = db.ask("What's our total revenue this month?")
```

## Connection Parameters

Alternatively, connect using the `Database.from_oracle()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_oracle(
    user="user",
    password="pass",
    host="localhost",
    port=1521,
    database="sales"
)

revenue = db.ask("What's our total revenue this month?")
```

::: toolfront.Database.from_oracle
    options:
      show_signature: false
      show_source: false
      show_root_heading: false
      show_root_toc_entry: false