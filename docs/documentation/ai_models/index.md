# AI Models

ToolFront supports various AI model providers through [Pydantic AI](https://ai.pydantic.dev/models/). You can use models from OpenAI, Anthropic, Google, Mistral, Cohere, and more.

## Basic Usage

All models are specified using the provider prefix format:

<div class="tabbed-set" markdown="1">

=== ":simple-openai:{ .middle } &nbsp; OpenAI"

    Export your API key:

    ```bash
    export OPENAI_API_KEY="your-openai-key"
    ```

    Then use the model:

    ```python
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    result = db.ask("Your question", model="openai:gpt-4o")
    ```

=== ":simple-anthropic:{ .middle } &nbsp; Anthropic"

    Export your API key:

    ```bash
    export ANTHROPIC_API_KEY="your-anthropic-key"
    ```

    Then use the model:

    ```python
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    result = db.ask("Your question", model="anthropic:claude-3-5-sonnet-20241022")
    ```

=== ":simple-google:{ .middle } &nbsp; Google"

    Export your API key:

    ```bash
    export GOOGLE_API_KEY="your-google-key"
    ```

    Then use the model:

    ```python
    from toolfront import Database

    db = Database("postgresql://user:pass@host/db")

    result = db.ask("Your question", model="google:gemini-1.5-pro")
    ```

</div>

## Setting Default Model

You can set a default model using the `TOOLFRONT_MODEL` environment variable:

<div class="tabbed-set" markdown="1">

=== ":simple-openai:{ .middle } &nbsp; OpenAI"

    ```bash
    export TOOLFRONT_MODEL="openai:gpt-4o"
    export OPENAI_API_KEY="your-openai-key"
    ```

=== ":simple-anthropic:{ .middle } &nbsp; Anthropic"

    ```bash
    export TOOLFRONT_MODEL="anthropic:claude-3-5-sonnet-20241022"
    export ANTHROPIC_API_KEY="your-anthropic-key"
    ```

=== ":simple-google:{ .middle } &nbsp; Google"

    ```bash
    export TOOLFRONT_MODEL="google:gemini-1.5-pro"
    export GOOGLE_API_KEY="your-google-key"
    ```

Then, use directly without specifying the model:

```python
from toolfront import Database

db = Database("postgresql://user:pass@host/db")

# Uses the model specified in TOOLFRONT_MODEL
result = db.ask("Your question")
```

</div>

## Custom Model Providers

You can use any Pydantic AI model provider and configuration with ToolFront:

<div class="tabbed-set" markdown="1">

=== ":fontawesome-solid-code-fork:{ .middle } &nbsp; OpenRouter"

    ```python
    from toolfront import Database
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openrouter import OpenRouterProvider

    openrouter_model = OpenAIChatModel(
        'anthropic/claude-3.5-sonnet',
        provider=OpenRouterProvider(api_key='your-openrouter-api-key'),
    )

    db = Database("postgres://user:pass@localhost:5432/mydb")
    answer = db.ask("What are our best-sellers?", model=openrouter_model)
    ```

=== ":simple-ollama:{ .middle } &nbsp; Ollama"

    ```python
    from toolfront import Database
    from pydantic_ai.models.openai import OpenAIChatModel

    ollama_model = OpenAIChatModel(
        'llama3.2',
        base_url='http://localhost:11434/v1',
        api_key='ignored',
    )

    db = Database("postgres://user:pass@localhost:5432/mydb")
    answer = db.ask("What's the revenue of our top-5 products", model=ollama_model)
    ```

=== ":simple-vercel:{ .middle } &nbsp; Vercel AI Gateway"

    ```python
    from toolfront import Database
    from pydantic_ai.models.openai import OpenAIChatModel

    vercel_model = OpenAIChatModel(
        'gpt-4o',
        base_url='https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_slug}/openai',
        api_key='your-openai-api-key',
    )

    db = Database("postgres://user:pass@localhost:5432/mydb")
    answer = db.ask("What's the revenue of our top-5 products", model=vercel_model)
    ```

</div>

For reference, see the [Pydantic AI model documentation](https://ai.pydantic.dev/models/), which includes the full list of OpenAI-compatible providers.