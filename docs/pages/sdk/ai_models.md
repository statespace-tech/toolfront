---
icon: lucide/brain-circuit
---

# AI Models

The SDK supports all major model providers through [Pydantic AI](https://ai.pydantic.dev/models/overview/).

To configure your model, start by export your provider's API key.

=== ":simple-openai:{ .middle } &nbsp; OpenAI"

    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.run(..., model="openai:gpt-5")
    ```

=== ":simple-anthropic:{ .middle } &nbsp; Anthropic"

    ```bash
    export ANTHROPIC_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.run(..., model="anthropic:claude-sonnet-4-5")
    ```

=== ":simple-google:{ .middle } &nbsp; Google"

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.run(..., model="google-gla:gemini-2.5-pro")
    ```

=== ":simple-mistralai:{ .middle } &nbsp; Mistral"

    ```bash
    export MISTRAL_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.run(..., model="mistral:mistral-large-latest")
    ```

=== ":simple-huggingface:{ .middle } &nbsp; HuggingFace"

    ```bash
    export HUGGINGFACE_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.run(..., model="huggingface:Qwen/Qwen3-235B-A22B")
    ```

=== ":material-source-branch:{ .middle } &nbsp; OpenRouter"

    ```bash
    export OPENROUTER_API_KEY="your-api-key"
    ```

    Then, specify your model using the `provider:model-name` format.

    ```python hl_lines="5"
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.run(..., model="openrouter:anthropic/claude-3.5-sonnet")
    ```

Alternatively, use [Pydantic AI](https://ai.pydantic.dev/models/overview/) directly for local or custom models.

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

    result = app.run(..., model=ollama_model)
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

    result = app.run(..., model=vercel_model)
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

    result = app.run(..., model=perplexity_model)
    ```

!!! tip "Tip: Default Model"

    Set a default model with the `TOOLFRONT_MODEL` environment variable: `export TOOLFRONT_MODEL="openai:gpt-5"`