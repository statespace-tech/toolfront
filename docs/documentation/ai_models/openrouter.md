# OpenRouter

## Setup

Get your API key from [OpenRouter](https://openrouter.ai/), and export it as an environment variable:

```bash
export OPENROUTER_API_KEY=<YOUR_OPENROUTER_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Google Gemini via OpenRouter
result = db.ask(..., model="openrouter:google/gemini-2.0-flash-exp")

# Anthropic Claude via OpenRouter
result = db.ask(..., model="openrouter:anthropic/claude-3.5-sonnet")
```


!!! tip "OpenRouter Model Names"
    Always specify an OpenRouter model with the `openrouter:` prefix.