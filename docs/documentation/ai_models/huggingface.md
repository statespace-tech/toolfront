# HuggingFace

## Setup

Get your access token from [Hugging Face](https://huggingface.co/settings/tokens) and export it as an environment variable:

```bash
export HF_TOKEN=<YOUR_HF_TOKEN>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Use any HuggingFace model
result = db.ask(..., model="huggingface:Qwen/Qwen3-235B-A22B")
```


!!! tip "HuggingFace Model Names"
    Always specify a HuggingFace model with the `huggingface:` prefix.