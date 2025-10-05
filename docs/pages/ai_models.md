# AI Models

ToolFront's [Python SDK](./python_sdk.md) supports various AI model providers through [Pydantic AI](https://ai.pydantic.dev/models/overview/).

[OpenAI](https://ai.pydantic.dev/models/openai/), [Anthropic](https://ai.pydantic.dev/models/anthropic/), [Google](https://ai.pydantic.dev/models/gemini/), [Bedrock](https://ai.pydantic.dev/models/bedrock/), [Cohere](https://ai.pydantic.dev/models/cohere/), [Groq](https://ai.pydantic.dev/models/groq/), [Mistral](https://ai.pydantic.dev/models/mistral/), [HuggingFace](https://ai.pydantic.dev/models/openai/#hugging-face), [xAI](https://ai.pydantic.dev/models/openai/#xai), [DeepSeek](https://ai.pydantic.dev/models/openai/#deepseek), [Azure AI](https://ai.pydantic.dev/models/openai/#azure), [Fireworks AI](https://ai.pydantic.dev/models/openai/#fireworks), [Moonshot AI](https://ai.pydantic.dev/models/openai/#moonshot), [GitHub Models](https://ai.pydantic.dev/models/openai/#github-models), [Heroku AI](https://ai.pydantic.dev/models/openai/#heroku), [OpenRouter](https://ai.pydantic.dev/models/openai/#openrouter), [Ollama](https://ai.pydantic.dev/models/openai/#ollama), [Together AI](https://ai.pydantic.dev/models/openai/#together-ai)

---

## Basic Usage

Set your model provider's API key as an environment variable, and then specify your Browser's model using the `provider:model-name` format.

=== ":simple-openai:{ .middle } &nbsp; OpenAI"

    ```bash
    export OPENAI_API_KEY="your-api-key"
    ```

    Pass the model to the browser:

    ```python hl_lines="3"
    from toolfront import Browser

    browser = Browser(model="openai:gpt-5")

    result = browser.ask("Your question", url="file:///path/to/toolsite")
    ```

=== ":simple-anthropic:{ .middle } &nbsp; Anthropic"

    ```bash
    export ANTHROPIC_API_KEY="your-api-key"
    ```

    Pass the model to the browser:

    ```python hl_lines="3"
    from toolfront import Browser

    browser = Browser(model="anthropic:claude-sonnet-4-5")

    result = browser.ask("Your question", url="file:///path/to/toolsite")
    ```

=== ":simple-google:{ .middle } &nbsp; Google"

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

    Pass the model to the browser:

    ```python hl_lines="3"
    from toolfront import Browser

    browser = Browser(model="google-gla:gemini-2.5-pro")

    result = browser.ask("Your question", url="file:///path/to/toolsite")
    ```

=== ":simple-mistralai:{ .middle } &nbsp; Mistral"

    ```bash
    export MISTRAL_API_KEY="your-api-key"
    ```

    Pass the model to the browser:

    ```python hl_lines="3"
    from toolfront import Browser

    browser = Browser(model="mistral:mistral-large-latest")

    result = browser.ask("Your question", url="file:///path/to/toolsite")
    ```

=== ":simple-huggingface:{ .middle } &nbsp; HuggingFace"

    ```bash
    export HUGGINGFACE_API_KEY="your-api-key"
    ```

    Pass the model to the browser:

    ```python hl_lines="3"
    from toolfront import Browser

    browser = Browser(model="huggingface:Qwen/Qwen3-235B-A22B")

    result = browser.ask("Your question", url="file:///path/to/toolsite")
    ```

!!! tip "Default Model"

    Set a default model with the `TOOLFRONT_MODEL` environment variable:

    ```bash
    export TOOLFRONT_MODEL="openai:gpt-5"
    ```

---

## Custom Providers

You can use any [Pydantic AI model](https://ai.pydantic.dev/models/overview/) directly for custom or local models.

```python
from toolfront import Browser
from pydantic_ai.models.openai import OpenAIChatModel

ollama_model = OpenAIChatModel(
    'llama3.2',
    base_url='http://localhost:11434/v1',
    api_key='ignored',
)

browser = Browser(model=ollama_model)

result = browser.ask("Your question", url="file:///path/to/toolsite")
```