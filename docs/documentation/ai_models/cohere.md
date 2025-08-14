# Cohere

## Setup

Get your API key from the [Cohere Dashboard](https://dashboard.cohere.ai/), and export it as an environment variable:

```bash
export CO_API_KEY=<YOUR_COHERE_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest Command R+ version
result = db.ask(..., model="cohere:command-r-plus")

# Pinned Command R+ version
result = db.ask(..., model="cohere:command-r-plus-08-2024")
```


!!! tip "Cohere Model Names"
    Always specify a Cohere model with the `cohere:` prefix.