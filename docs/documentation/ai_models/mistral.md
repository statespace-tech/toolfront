# Mistral

## Setup

Get your API key from the [Mistral AI Platform](https://console.mistral.ai/), and export it as an environment variable:

```bash
export MISTRAL_API_KEY=<YOUR_MISTRAL_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest Mistral Large version
result = db.ask(..., model="mistral:mistral-large-latest")
```


!!! tip "Mistral Model Names"
    Always specify a Mistral model with the `mistral:` prefix.