# BigQuery

## Installation

```bash
pip install "toolfront[bigquery]"
```

## Connection URL

Connect to BigQuery by passing a connection URL to the `Database` constructor:

```python linenums="1" hl_lines="3"
from toolfront import Database

db = Database(url="bigquery://{project_id}/{dataset_id}")

revenue = db.ask("What's our total revenue this month?")
```

## Connection Parameters

Alternatively, connect using the `Database.from_bigquery()` method with parameters:

```python linenums="1"
from toolfront import Database

db = Database.from_bigquery(
    project_id="my-project",
    dataset_id="sales",
    location="us-west1"
)

revenue = db.ask("What's our total revenue this month?")
```