# Groq

## Setup

Get your API key from the [Groq Console](https://console.groq.com/), and export it as an environment variable:

```bash
export GROQ_API_KEY=<YOUR_GROQ_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest Llama 3.3 70B version
result = db.ask(..., model="groq:llama-3.3-70b-versatile")
```


!!! tip "Groq Model Names"
    Always specify a Groq model with the `groq:` prefix.