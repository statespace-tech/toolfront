# GitHub Models

## Setup

Get your API key from [GitHub Models](https://github.com/marketplace/models), and export it as an environment variable:

```bash
export GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# GPT-4o via GitHub Models
result = db.ask(..., model="github:gpt-4o")

# Claude via GitHub Models
result = db.ask(..., model="github:claude-3-5-sonnet")
```


!!! tip "GitHub Model Names"
    Always specify a GitHub model with the `github:` prefix.