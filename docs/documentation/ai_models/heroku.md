# Heroku AI

## Setup

Configure your Heroku AI deployment and export the endpoint as an environment variable:

```bash
export HEROKU_INFERENCE_KEY=<YOUR_HEROKU_API_KEY>
export HEROKU_INFERENCE_URL=<YOUR_HEROKU_ENDPOINT>
```

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Custom model deployed on Heroku
result = db.ask(..., model="heroku:custom-model")

# OpenAI-compatible model on Heroku
result = db.ask(..., model="heroku:gpt-3.5-turbo")
```


!!! tip "Heroku Model Names"
    Always specify a Heroku model with the `heroku:` prefix.