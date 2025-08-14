# Together AI

## Setup

Get your API key from [Together AI](https://www.together.ai/), and export it as an environment variable:

```bash
export TOGETHER_API_KEY=<YOUR_TOGETHER_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Meta Llama model via Together AI
result = db.ask(..., model="together:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

# Qwen model via Together AI
result = db.ask(..., model="together:Qwen/Qwen2.5-72B-Instruct-Turbo")
```


!!! tip "Together AI Model Names"
    Always specify a Together AI model with the `together:` prefix.