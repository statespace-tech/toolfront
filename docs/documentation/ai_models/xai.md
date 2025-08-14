# xAI

## Setup

Get your API key from the [xAI Console](https://console.x.ai/), and export it as an environment variable:

```bash
export GROK_API_KEY=<GROK_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest Grok version
result = db.ask(..., model="grok:grok-2-1212")
```


!!! tip "xAI Model Names"
    Always specify an xAI model with the `grok:` prefix.