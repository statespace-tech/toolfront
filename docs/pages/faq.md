# FAQ

**When should I use the Python SDK vs MCP Server?**

Use the Python SDK to run applications directly with built-in agents. Use the MCP Server to connect your own agents (like Claude Desktop or Cline) to applications.

**Can I use ToolFront with any AI model?**

Yes! The Python SDK works with any model through **[Pydantic AI](https://ai.pydantic.dev/models/overview/)**, including cloud providers (OpenAI, Anthropic, Google, Mistral) and local models (Ollama, LM Studio).

**How do I deploy applications?**

You can run applications from local directories, host them on your own infrastructure, or deploy them to **[ToolFront Cloud](toolfront_cloud.md)** for remote access.

**Are my ToolFront Cloud applications private?**

Yes! ToolFront Cloud hosts your project files over HTTPS with API key authentication. Your agents can access applications like any other remote resource.

**Why is search only available with ToolFront Cloud?**

The `search` tool requires BM25 indexing, which happens automatically when you deploy to ToolFront Cloud. Local applications can still use `grep` and `glob` for searching.
