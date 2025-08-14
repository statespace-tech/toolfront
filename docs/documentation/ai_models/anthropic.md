# Anthropic

## Setup

Get your API key from the [Anthropic Console](https://console.anthropic.com/), and export it as an environment variable:

```bash
export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest Claude 3.5 Sonnet version
result = db.ask(..., model="anthropic:claude-3-5-sonnet-latest")

# Pinned Claude 3.5 Sonnet version
result = db.ask(..., model="anthropic:claude-3-5-sonnet-20241022")
```


!!! tip "Anthropic Model Names"
    Always specify an Anthropic model with the `anthropic:` prefix.