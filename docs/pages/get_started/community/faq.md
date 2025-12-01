---
icon: lucide/message-circle-question-mark
---
# FAQ

## Why Markdown?

Markdown is simple, readable, and works with version control. You can define both instructions and tools in one place without learning new syntax. Just add more `.md` files to extend your app.

## How is ToolFront different from MCPs?

  | | MCPs | ToolFront |
  |---|------|-----------|
  | **Implementation** | Code | Markdown |
  | **Tool discovery** | Upfront[^1] | Progressive |
  | **Connection** | Stateful stdio/SSE | Stateless HTTP |

## How is ToolFront different from other RAG frameworks?

Other frameworks provide RAG components like embedders, chunkers, retrievers, and APIs. ToolFront helps you composes them into apps.

## When should I use the CLI, SDK, or MCP?

Use the [command line](../../documentation/integration/command_line.md) for rapid testing and development, the [Python SDK](../../documentation/integration/python_sdk.md) to query apps in Python, and the [MCP Server](../../documentation/integration/mcp_server.md) to connect them to MCP clients like Cursor and Claude Code.

## Can I use ToolFront with any AI model?

Yes! The Python SDK works with any model through [Pydantic AI](https://ai.pydantic.dev/models/overview/). This includes cloud providers (OpenAI, Anthropic, Google, Mistral) as well as local models (Ollama, LM Studio).

## How do I deploy applications?

You can self-host applications or use Statespace to deploy public or private apps to the cloud. Start by creating a free [Statespace account](#)[^2].


[^1]: Loading all tool definitions upfront slows down agents and increases costs. See [Anthropic's blog post](https://www.anthropic.com/engineering/code-execution-with-mcp).
[^2]: Statespace is currently in beta. Email `esteban[at]statespace[dot]com` or join our [Discord](https://discord.gg/rRyM7zkZTf) to get an API key.