# FAQ

**What is an environment?**

An environment is a directory with Markdown files that define tasks, instructions, and tools for AI agents. Agents browse environments to complete work.

**Where do my agents run?**

Agents run anywhere: locally, in the cloud, or on edge devices. We recommend separating agents from environments so you can modify and scale each component independently.

**When should I use the Python SDK vs MCP Server?**

Use the **[Python SDK](/pages/python_sdk/)** to quickly build and run Python agents. Use the **[MCP Server](/pages/mcp_server/)** to connect your own agents (like Claude Desktop or Cline) to environments.

**Can I use ToolFront with any AI model?**

Yes! The Python SDK works with any model through **[Pydantic AI](https://ai.pydantic.dev/models/overview/)**, including cloud providers (OpenAI, Anthropic, Google, Mistral) and local models (Ollama, LM Studio).

**How do I deploy environments?**

You can run environments locally, host them on your own infrastructure, or securely deploy them to **[ToolFront Cloud](/pages/toolfront_cloud/)** for remote access.

**Are my ToolFront Cloud environments private?**

Yes! ToolFront Cloud hosts environments over HTTPS with API key authentication. You agents can then access your environments like any other API.

**Why is search only available with ToolFront Cloud?**

The `search` tool requires BM25 indexing, which happens automatically when you deploy to ToolFront cloud. Local environments can still use `grep` and `glob` for searching.
