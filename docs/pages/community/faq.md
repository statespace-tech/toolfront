---
icon: lucide/message-circle-question-mark
---
# FAQ

## How is ToolFront different from MCPs or Agent Skills?

  | | MCPs | Agent Skills | ToolFront |
  |---|------|--------|-----------|
  | **Implementation** | code | Markdown | Markdown |
  | **Context** | ✗ | ✓ | ✓ |
  | **Tools** | ✓ | ✗ | ✓ |
  | **Discovery** | upfront[^1] | progressive | progressive |
  | **Connection** | stateful stdio/SSE | local filesystem | stateless HTTP |

## How is ToolFront different from RAG or agent frameworks?

RAG frameworks provide components (embedders, chunkers, retrievers, vector databases) that you can compose into ToolFront apps, share, and use to and power agents with your ow own agent frameworks

## Can I use ToolFront with any AI agent?

Yes! Most coding agents (Claude Code, GitHub Copilot, Codex) work out of the box. Custom agents just need an HTTP request tool to interact with ToolFront applications.

[^1]: Loading all tool definitions upfront slows down agents and increases costs. See [Anthropic's blog post](https://www.anthropic.com/engineering/code-execution-with-mcp).