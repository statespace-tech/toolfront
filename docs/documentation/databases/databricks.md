# Databricks

## Installation

```bash
pip install "toolfront[databricks]"
```

## Connection Parameters

Connect using the `Database.from_databricks()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_databricks(
    server_hostname="workspace.databricks.com",
    http_path="/sql/1.0/warehouses/warehouse-id",
    access_token="token",
    catalog="sales"
)

revenue = db.ask("What's our total revenue this month?")
```