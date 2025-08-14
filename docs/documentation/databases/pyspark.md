# PySpark

## Installation

```bash
pip install "toolfront[pyspark]"
```

## Connection Parameters

Connect using the `Database.from_pyspark()` method with parameters:

```python linenums="1"
from toolfront import Database
from pyspark.sql import SparkSession

# Create PySpark SparkSession
session = SparkSession.builder.getOrCreate()

db = Database.from_pyspark(
    session=session,
    mode="batch"
)

revenue = db.ask("What's our total revenue this month?")
```

::: toolfront.Database.from_pyspark
    options:
      show_signature: false
      show_source: false
      show_root_heading: false
      show_root_toc_entry: false