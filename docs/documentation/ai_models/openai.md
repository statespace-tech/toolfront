# OpenAI

## Setup

Get your API key from the [OpenAI Platform](https://platform.openai.com/api-keys), and export is as an environment variable:

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest GPT-4o version
result = db.ask(..., model="openai:gpt-4o")

# Pinned GPT-4o version
result = db.ask(..., model="openai:gpt-4o-2024-11-20")
```


!!! tip "OpenAI Model Names"
    Always specify an OpenAI model with the `openai:` prefix.
