# DeepSeek

## Setup

Get your API key from the [DeepSeek Platform](https://platform.deepseek.com/), and export it as an environment variable:

```bash
export DEEPSEEK_API_KEY=<YOUR_DEEPSEEK_API_KEY>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest DeepSeek Chat version
result = db.ask(..., model="deepseek:deepseek-chat")
```


!!! tip "DeepSeek Model Names"
    Always specify a DeepSeek model with the `deepseek:` prefix.