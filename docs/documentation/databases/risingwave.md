# RisingWave

## Installation

```bash
pip install "toolfront[risingwave]"
```

## Connection Parameters

Connect using the `Database.from_risingwave()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_risingwave(
    host="localhost",
    port=5432,
    database="sales",
    user="user",
    password="pass",
    schema="public"
)

revenue = db.ask("What's our total revenue this month?")
```