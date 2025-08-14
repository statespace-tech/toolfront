# Fireworks AI

## Setup

Get your API key from the [Fireworks AI Console](https://fireworks.ai/), and export it as an environment variable:

```bash
export FIREWORKS_API_KEY=<YOUR_FIREWORKS_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest Llama model version
result = db.ask(..., model="fireworks:accounts/fireworks/models/llama-v3p1-70b-instruct")

# Code generation model
result = db.ask(..., model="fireworks:accounts/fireworks/models/deepseek-coder-v2-lite-instruct")
```


!!! tip "Fireworks AI Model Names"
    Always specify a Fireworks AI model with the `fireworks:` prefix.