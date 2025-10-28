# Documentation

This page provides detailed documentation for ToolFront's core features: declaring tools in Markdown frontmatters, using the Python SDK to run applications programmatically, and setting up the MCP server to connect agents to your applications.

---

## Tools

Tools are commands that AI agents can call to take actions. 
They can be standard CLI programs like `grep` and `curl`, or custom scripts written in any language.

```markdown title="page.md"
---
tools:
  - [grep]
  - [curl]
  - [python3, script.py]

---

Call the tools to ...
```

There are three ways to pass variables to tools:

=== ":material-code-braces:{ .middle } &nbsp; `{parameters}`"

    ```markdown hl_lines="3"
    ---
    tools:
      - [curl, "https://api.com/products/{product_id}"]
      - [gh, issue, create]
      - [stripe, products, list, --api-key, $STRIPE_KEY]

    ---

    Call the tools to ...
    ```

    Agents automatically replace placeholders with actual values when calling tools.

    ```bash
    Calling "curl https://api.com/products/prod-123"
    ```


    !!! tip "Parameter Instructions"
        Provide clear instructions to your agent in the Markdown body explaining how to fill in and pass the tool parameters.


=== ":material-flag:{ .middle } &nbsp; `--arguments`"

    ```markdown hl_lines="4"
    ---
    tools:
      - [curl, "https://api.com/products/{product_id}"]
      - [gh, issue, create]
      - [stripe, products, list, --api-key, $STRIPE_KEY]

    ---

    Call the tools to ...
    ```

    Agents can append arguments like flags and options to tool calls.

    ```bash
    Calling "gh issue create --title 'Bug report' --repo owner/repo"
    ```

    !!! tip "Learning Tools"
        Agents learn how to use tools by passing the `--help` flag.

    

=== ":material-variable:{ .middle } &nbsp; `$ENV_VARIABLES`"

    ```markdown hl_lines="5"
    ---
    tools:
      - [curl, "https://api.com/products/{product_id}"]
      - [gh, issue, create]
      - [stripe, products, list, --api-key, $STRIPE_KEY]

    ---

    Call the tools to ...
    ```

    Include environment variables to keep credentials and configurations private.

    ```bash
    Calling "stripe products list --api-key sk_fake_placeholder_key"
    ```

    !!! warning "Managing secrets"
        Use environment variables to prevent exposing secrets to LLMs

---

## Python SDK

ToolFront's Python SDK provides a simple interface for running AI applications programmatically. It supports all major model providers through Pydantic AI, with built-in structured output.

```python
from toolfront import Application

app = Application(url=" http://127.0.0.1:8000")

result = app.run(
    prompt="Email coupons to customers who made purchases last month",
    model="openai:gpt-5"
)
# Returns: "Done!"
```

---

### AI Models

The SDK supports all major model providers through [Pydantic AI](https://ai.pydantic.dev/models/overview/). Start by exporting your API key.

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

!!! tip "Tip: Default Model"

    Set a default model with the `TOOLFRONT_MODEL` environment variable: `export TOOLFRONT_MODEL="openai:gpt-5"`


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

---

### Structured Output

Retrieve structured data in any format by using the `output_type` parameter.

=== ":fontawesome-solid-cube:{ .middle } &nbsp; Scalars"

    ```python
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    avg_price = app.run(
        prompt="What's our average ticket price?",
        model="openai:gpt-5",
        output_type=float
    )
    # Returns: 29.99

    has_inventory = app.run(
        prompt="Do we have any monitors in stock?",
        model="openai:gpt-5",
        output_type=bool
    )
    # Returns: True
    ```

=== ":fontawesome-solid-layer-group:{ .middle } &nbsp; Collections"

    ```python
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    product_names = app.run(
        "What products do we sell?",
        model="openai:gpt-5",
        output_type=list[str]
    )
    # Returns: ["Laptop Pro", "Wireless Mouse", "USB Cable"]

    sales_by_region = app.run(
        "Sales by region",
        model="openai:gpt-5",
        output_type=dict[str, int]
    )
    # Returns: {"North": 45000, "South": 38000, "East": 52000}
    ```

=== ":fontawesome-solid-chain:{ .middle } &nbsp; Unions"

    ```python
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    result = app.run(
        "Best-sellers this month?",
        model="openai:gpt-5",
        output_type=str | list[str]
    )
    # Returns: ["Product A", "Product B"] or "No data found"

    error = app.run(
        "What was the error message?",
        model="openai:gpt-5",
        output_type=str | None
    )
    # Returns: "Connection timeout" or None
    ```

=== ":fontawesome-solid-sitemap:{ .middle } &nbsp; Objects"

    ```python
    from toolfront import Application
    from pydantic import BaseModel, Field

    app = Application(url=" http://127.0.0.1:8000")

    class Product(BaseModel):
        name: str = Field(description="Product name")
        price: float = Field(description="Product price in USD")
        in_stock: bool = Field(description="Whether product is in stock")


    product = app.run(
        "What's our best-selling product?",
        model="openai:gpt-5",
        output_type=Product
    )
    # Returns: Product(name="Blue Headphones", price=300.0, in_stock=True)
    ```

=== ":fontawesome-solid-percent:{ .middle } &nbsp; Functions"

    ```python
    from toolfront import Application

    app = Application(url=" http://127.0.0.1:8000")

    def my_func(price: float, quantity: int):
        """
        Returns a product's revenue based on price and quantity sold
        """
        return price * quantity

    # Returns the output of the provided function
    product = app.run(
        "Compute the revenue of our best-seller",
        model="openai:gpt-5",
        output_type=my_func
    )
    # Returns: 127.000
    ```

---

## MCP Server

ToolFront's MCP (Model Context Protocol) server exposes your applications as tools for AI agents in MCP-compatible clients like Claude Desktop and Cline. The server supports multiple transport protocols (stdio, HTTP, SSE) and can be configured via JSON or run directly from the command line.

=== ":material-code-json:{ .middle } &nbsp; JSON"

    Configure MCP clients like Claude Desktop or Cline.

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", " http://127.0.0.1:8000"]
        }
      }
    }
    ```

=== ":material-console:{ .middle } &nbsp; CLI"

    Run the server directly from the command line.

    ```bash
    toolfront mcp  http://127.0.0.1:8000
    ```

Available options:

- `--transport` - Communication protocol: `stdio` (default), `streamable-http`, or `sse`
- `--host` - Server host address (default: `127.0.0.1`)
- `--port` - Server port number (default: `8000`)
- `--params` / `-p` - Authentication for remote application (e.g., `--params KEY=value`)
- `--env` - Environment variables for tools (e.g., `--env TOKEN=value`)

---

::: toolfront.application.Application
    options:
      show_root_heading: true
      show_source: true
      members: []

::: toolfront.application.Application.ask
    options:
      show_root_heading: true
      show_source: true