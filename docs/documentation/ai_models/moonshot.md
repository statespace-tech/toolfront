# Moonshot AI

## Setup

Get your API key from [Moonshot AI](https://platform.moonshot.cn/) and export it as an environment variable:

```bash
export MOONSHOT_API_KEY=<YOUR_MOONSHOT_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Moonshot v1 model
result = db.ask(..., model="moonshot:moonshot-v1-8k")
```


!!! tip "Moonshot Model Names"
    Always specify a Moonshot model with the `moonshot:` prefix.