# Snowflake

## Installation

```bash
pip install "toolfront[snowflake]"
```

## Connection URL

Connect to Snowflake by passing a connection URL to the `Database` constructor:

```python linenums="1" hl_lines="3"
from toolfront import Database

db = Database(url="snowflake://{user}:{password}@{account}/{database}")

revenue = db.ask("What's our total revenue this month?")
```

## Connection Parameters

Alternatively, connect using the `Database.from_snowflake()` method with parameters:

```python linenums="1"
from toolfront import Database 

db = Database.from_snowflake(
    user="user",
    account="account-id", 
    database="sales",
    password="pass",
    authenticator="snowflake"
)

revenue = db.ask("What's our total revenue this month?")
```