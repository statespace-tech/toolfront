# Python SDK

ToolFront's SDK lets you quickly build and run Python agents on environments. 


```python
from toolfront import Environment

env = Environment(url="file:///path/toolsite")

result = env.run(
    prompt="Email coupons to customers who made purchases last month", 
    model="openai:gpt-5"
)
# Returns: "Done!"
```

!!! question "How does it work?"
    The SDK connects local [Pydantic AI](https://ai.pydantic.dev/models/overview/) models to environments through the [MCP server](/pages/mcp_server/).

--- 

## AI Models

The SDK works with any model providers through [Pydantic AI](https://ai.pydantic.dev/models/overview/). Start by exporting your API key.

=== ":simple-openai:{ .middle } &nbsp; OpenAI"

    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Environment

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model="openai:gpt-5")
    ```

=== ":simple-anthropic:{ .middle } &nbsp; Anthropic"

    ```bash
    export ANTHROPIC_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Environment

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model="anthropic:claude-sonnet-4-5")
    ```

=== ":simple-google:{ .middle } &nbsp; Google"

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Environment

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model="google-gla:gemini-2.5-pro")
    ```

=== ":simple-mistralai:{ .middle } &nbsp; Mistral"

    ```bash
    export MISTRAL_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Environment

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model="mistral:mistral-large-latest")
    ```

=== ":simple-huggingface:{ .middle } &nbsp; HuggingFace"

    ```bash
    export HUGGINGFACE_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Environment

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model="huggingface:Qwen/Qwen3-235B-A22B")
    ```

=== ":material-source-branch:{ .middle } &nbsp; OpenRouter"

    ```bash
    export OPENROUTER_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Environment

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model="openrouter:anthropic/claude-3.5-sonnet")
    ```

!!! tip "Tip: Default Model"

    Configure a default model for all your runs:

    ```bash
    export TOOLFRONT_MODEL="openai:gpt-5"
    ```


Alternatively, use [Pydantic AI](https://ai.pydantic.dev/models/overview/) models directly.

=== ":simple-ollama:{ .middle } &nbsp; Ollama"

    ```python
    from toolfront import Environment
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.ollama import OllamaProvider

    ollama_model = OpenAIChatModel(
        model_name='llama3.2',
        provider=OllamaProvider(base_url='http://localhost:11434/v1'),
    )

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model=ollama_model)
    ```

=== ":simple-vercel:{ .middle } &nbsp; Vercel"

    ```python
    from toolfront import Environment
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.vercel import VercelProvider

    vercel_model = OpenAIChatModel(
        'anthropic/claude-4-sonnet',
        provider=VercelProvider(api_key='your-vercel-ai-gateway-api-key'),
    )

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model=vercel_model)
    ```

=== ":simple-perplexity:{ .middle } &nbsp; Perplexity"

    ```python
    from toolfront import Environment
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    perplexity_model = OpenAIChatModel(
        'sonar-pro',
        provider=OpenAIProvider(
            base_url='https://api.perplexity.ai',
            api_key='your-perplexity-api-key',
        )
    )

    environment = Environment(url="file:///path/to/toolsite")

    result = environment.ask(..., model=perplexity_model)
    ```

---

## Structured Retrieval

Use `output_type` to get retrieve structured data in any format you need.

=== ":fontawesome-solid-cube:{ .middle } &nbsp; Scalars"

    ```python
    from toolfront import Environment

    environment = Environment(url="file:///path/toolsite")

    avg_price = environment.run(
        prompt="What's our average ticket price?",
        model="openai:gpt-5",
        output_type=float
    )
    # Returns: 29.99

    has_inventory = environment.run(
        prompt="Do we have any monitors in stock?",
        model="openai:gpt-5",
        output_type=bool
    )
    # Returns: True
    ```

=== ":fontawesome-solid-layer-group:{ .middle } &nbsp; Collections"

    ```python
    from toolfront import Environment

    environment = Environment(url="file:///path/toolsite")

    product_names = environment.run(
        "What products do we sell?",
        model="openai:gpt-5",
        output_type=list[str]
    )
    # Returns: ["Laptop Pro", "Wireless Mouse", "USB Cable"]

    sales_by_region = environment.run(
        "Sales by region",
        model="openai:gpt-5",
        output_type=dict[str, int]
    )
    # Returns: {"North": 45000, "South": 38000, "East": 52000}
    ```

=== ":fontawesome-solid-chain:{ .middle } &nbsp; Unions"

    ```python
    from toolfront import Environment

    environment = Environment(url="file:///path/toolsite")

    result = environment.run(
        "Best-sellers this month?",
        model="openai:gpt-5",
        output_type=str | list[str]
    )
    # Returns: ["Product A", "Product B"] or "No data found"

    error = environment.run(
        "What was the error message?",
        model="openai:gpt-5",
        output_type=str | None
    )
    # Returns: "Connection timeout" or None
    ```

=== ":fontawesome-solid-sitemap:{ .middle } &nbsp; Objects"

    ```python
    from toolfront import Environment
    from pydantic import BaseModel, Field

    environment = Environment(url="file:///path/toolsite")

    class Product(BaseModel):
        name: str = Field(description="Product name")
        price: float = Field(description="Product price in USD")
        in_stock: bool = Field(description="Whether product is in stock")


    product = environment.run(
        "What's our best-selling product?",
        model="openai:gpt-5",
        output_type=Product
    )
    # Returns: Product(name="Blue Headphones", price=300.0, in_stock=True)
    ```

=== ":fontawesome-solid-percent:{ .middle } &nbsp; Functions"

    ```python
    from toolfront import Environment

    environment = Environment(url="file:///path/toolsite")

    def my_func(price: float, quantity: int):
        """
        Returns a product's revenue of based on price and quantity sold
        """
        return price * quantity

    # Returns the output of the provided function
    product = environment.run(
        "Compute the revenue of our best-seller",
        model="openai:gpt-5",
        output_type=my_func
    )
    # Returns: 127.000
    ```

---

## Environment Variables

Markdown pages may reference environment variables for authentication or configuration:

```markdown hl_lines="3-4"
---
tools:
  - [curl, -X, GET, "https://api.com/data", -H, "Authorization: Bearer $TOKEN"]
  - [toolfront, database, $DB_URL]

---

# My Markdown page
...
```

Pass these variables to the `Environment` using the `env` parameter.

```python
from toolfront import Environment

environment = Environment(
    url="file:///path/toolsite",
    env={
        "TOKEN": "token",
        "DB_URL": "postgresql://user:pass@localhost:5432/mydb"
    }
)

result = environment.run("Fetch latest data", model="openai:gpt-5")
```

!!! warning "Working with Secrets"
    Environment variables are never exposed to AI agents.

---

::: toolfront.environment.Environment
    options:
      show_root_heading: true
      show_source: true
      members: []

::: toolfront.environment.Environment.run
    options:
      show_root_heading: true
      show_source: true