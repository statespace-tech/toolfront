# Google

## Setup

Get your API key from [Google AI Studio](https://aistudio.google.com/), and export it as an environment variable:

```bash
export GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
```

Google Gemini models can be accessed through two different providers:

- **`google-gla:`** - Google Generative Language API (standard)
- **`google-vertex:`** - Google Vertex AI platform

## Examples


```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Latest Gemini 2.0 Flash version (GLA)
result = db.ask(..., model="google-gla:gemini-2.0-flash-exp")

# Latest Gemini 2.0 Flash version (Vertex AI)
result = db.ask(..., model="google-vertex:gemini-2.0-flash-exp")

# Pinned Gemini version
result = db.ask(..., model="google-gla:gemini-1.5-pro-002")
```


!!! tip "Google Model Names"
    Always specify a Google model with either the `google-gla:` or `google-vertex:` prefix.