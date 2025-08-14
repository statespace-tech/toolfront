# Azure AI

## Setup

Set your Azure OpenAI API key, endpoint, and optional API version:

```bash
export AZURE_OPENAI_API_KEY=<YOUR_AZURE_OPENAI_API_KEY>
export AZURE_OPENAI_ENDPOINT=<YOUR_AZURE_OPENAI_ENDPOINT>
export OPENAI_API_VERSION=<YOUR_OPENAI_API_VERSION>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# GPT-4 via Azure OpenAI
result = db.ask(..., model="azure:gpt-4o")
```


!!! tip "Azure OpenAI Model Names"
    Always specify an Azure OpenAI model with the `azure:` prefix.