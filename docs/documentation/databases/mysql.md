# MySQL

## Installation

```bash
pip install "toolfront[mysql]"
```

## Connection URL

Connect to MySQL by passing a connection URL to the `Database` constructor:

```python linenums="1" hl_lines="3"
from toolfront import Database

db = Database(url="mysql://{user}:{password}@{host}:{port}/{database}")

revenue = db.ask("What's our total revenue this month?")
```

## Connection Parameters

Alternatively, connect using the `Database.from_mysql()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_mysql(
    host="localhost",
    port=3306,
    database="sales",
    user="user",
    password="pass"
)

revenue = db.ask("What's our total revenue this month?")
```