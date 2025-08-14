# Flink

## Installation

```bash
pip install "toolfront[flink]"
```

## Connection Parameters

Connect using the `Database.from_flink()` method with parameters:

```python linenums="1"
from toolfront import Database
from pyflink.table import EnvironmentSettings, TableEnvironment

# Create PyFlink TableEnvironment
table_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())

db = Database.from_flink(table_env=table_env)

revenue = db.ask("What's our total revenue this month?")
```

::: toolfront.Database.from_flink
    options:
      show_signature: false
      show_source: false
      show_root_heading: false
      show_root_toc_entry: false