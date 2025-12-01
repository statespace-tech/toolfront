---
icon: simple/python
---

# Python SDK

ToolFront's SDK provides a simple interface for interacting with RAG applications in Python.

## Basic usage

Create an `Application` instance with your application's URL and call the `ask` method.

```python
from toolfront import Application

app = Application(url=" http://127.0.0.1:8000")

result = app.ask(prompt="Email coupons to our best customers", model="openai:gpt-5")

print(result)
```

## AI models

### Cloud providers

The SDK supports all major model cloud providers through [Pydantic AI](https://ai.pydantic.dev/models/overview/).


=== ":simple-openai:{ .middle } &nbsp; OpenAI"

    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

    Specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model="openai:gpt-5")
    ```

=== ":simple-anthropic:{ .middle } &nbsp; Anthropic"

    ```bash
    export ANTHROPIC_API_KEY="your-api-key"
    ```

    Specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model="anthropic:claude-sonnet-4-5")
    ```

=== ":simple-google:{ .middle } &nbsp; Google"

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

    Specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model="google-gla:gemini-2.5-pro")
    ```

=== ":simple-mistralai:{ .middle } &nbsp; Mistral"

    ```bash
    export MISTRAL_API_KEY="your-api-key"
    ```

    Specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model="mistral:mistral-large-latest")
    ```

=== ":simple-huggingface:{ .middle } &nbsp; HuggingFace"

    ```bash
    export HUGGINGFACE_API_KEY="your-api-key"
    ```

    Specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model="huggingface:Qwen/Qwen3-235B-A22B")
    ```

=== ":material-source-branch:{ .middle } &nbsp; OpenRouter"

    ```bash
    export OPENROUTER_API_KEY="your-api-key"
    ```

    Specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model="openrouter:anthropic/claude-3.5-sonnet")
    ```

### Local and custom models

Use [Pydantic AI](https://ai.pydantic.dev/models/overview/) directly for local or custom models.

=== ":simple-ollama:{ .middle } &nbsp; Ollama"

    ```python
    from toolfront import Application
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.ollama import OllamaProvider

    ollama_model = OpenAIChatModel(
        model_name='llama3.2',
        provider=OllamaProvider(base_url='http://localhost:11434/v1'),
    )

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model=ollama_model)
    ```

=== ":simple-vercel:{ .middle } &nbsp; Vercel"

    ```python
    from toolfront import Application
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.vercel import VercelProvider

    vercel_model = OpenAIChatModel(
        'anthropic/claude-4-sonnet',
        provider=VercelProvider(api_key='your-vercel-ai-gateway-api-key'),
    )

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model=vercel_model)
    ```

=== ":simple-perplexity:{ .middle } &nbsp; Perplexity"

    ```python
    from toolfront import Application
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    perplexity_model = OpenAIChatModel(
        'sonar-pro',
        provider=OpenAIProvider(
            base_url='https://api.perplexity.ai',
            api_key='your-perplexity-api-key',
        )
    )

    app = Application(url=" http://127.0.0.1:8000")

    result = app.ask(..., model=perplexity_model)
    ```

### Default model

Set a default model using the `TOOLFRONT_MODEL` environment variable.
    
```bash
export TOOLFRONT_MODEL="openai:gpt-5"
```

## Structured output

### Scalars

Extract primitive values such as numbers, strings, and booleans.

```python hl_lines="8 15"
from toolfront import Application

app = Application(url=" http://127.0.0.1:8000")

avg_price = app.ask(
    prompt="What's our average ticket price?",
    model="openai:gpt-5",
    output_type=float
)
# Example return: 29.99

has_inventory = app.ask(
    prompt="Do we have any monitors in stock?",
    model="openai:gpt-5",
    output_type=bool
)
# Example return: True
```

### Collections

Extract structured data as lists and dictionaries.

```python hl_lines="8 15"
from toolfront import Application

app = Application(url=" http://127.0.0.1:8000")

product_names = app.ask(
    "What products do we sell?",
    model="openai:gpt-5",
    output_type=list[str]
)
# Example return: ["Laptop Pro", "Wireless Mouse", "USB Cable"]

sales_by_region = app.ask(
    "Sales by region",
    model="openai:gpt-5",
    output_type=dict[str, int]
)
# Example return: {"North": 45000, "South": 38000, "East": 52000}
```

### Unions

Handle multiple possible return types or optional values.

```python hl_lines="8 15"
from toolfront import Application

app = Application(url=" http://127.0.0.1:8000")

result = app.ask(
    "Best-sellers this month?",
    model="openai:gpt-5",
    output_type=str | list[str]
)
# Example return: ["Product A", "Product B"] or "No data found"

error = app.ask(
    "What was the error message?",
    model="openai:gpt-5",
    output_type=str | None
)
# Example return: "Connection timeout" or None
```

### Objects

Define complex output data structures with Pydantic models.

```python hl_lines="15"
from toolfront import Application
from pydantic import BaseModel, Field

app = Application(url=" http://127.0.0.1:8000")

class Product(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Product price in USD")
    in_stock: bool = Field(description="Whether product is in stock")


product = app.ask(
    "What's our best-selling product?",
    model="openai:gpt-5",
    output_type=Product
)
# Example return: Product(name="Blue Headphones", price=300.0, in_stock=True)
```

### Functions

Call custom functions and return their output.

```python hl_lines="15"
from toolfront import Application

app = Application(url=" http://127.0.0.1:8000")

def my_func(price: float, quantity: int):
    """Calculate product revenue based on price and quantity sold."""
    return price * quantity

# The model extracts parameters and executes the function
revenue = app.ask(
    "Compute the revenue of our best-seller",
    model="openai:gpt-5",
    output_type=my_func
)
# Example return: 127000.0
```

## Environment variables

Provide environment variables through the `env` parameter when instantiating your application.

```python hl_lines="5-9"
from toolfront import Application

app = Application(
    url="http://127.0.0.1:8000",
    env={
        "API_KEY": "sk-...",
        "USER": "admin",
        "DATABASE": "production"
    }
)

result = app.ask(
    prompt="Query the database for active users",
    model="openai:gpt-5"
)
```

!!! question "Learn more"
    See the [tools documentation](../../reference/client_library/cli_commands.md) for  how to define environment variables in your tools.