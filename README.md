[![Test Suite](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square)](https://discord.gg/rRyM7zkZTf)
[![X](https://img.shields.io/badge/ToolFront-black?style=flat-square&logo=x&logoColor=white)](https://x.com/toolfront)

<br>
<div align="center"> 
<img alt="toolfront" src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/logo.png" width="61.8%">
</div>
<br>

<br>

> Without context, It's hard for AI to answer questions about your databases. 
> However, teaching them your table schemas and relationships is a slow, manual, and expensive process. ToolFront connects AI agents to your databases, so they can learn your query patterns as they navigate your databases.

## Features

- **🚀 One-step setup**: Connect AI agents like Cursor, Copilot, and Claude to all your databases with a single command.
- **🤖 Agents for your data:** Build smart agents that understand your databases and know how to navigate them.
- **⚡ AI-powered DataOps:** Use ToolFront to explore your databases, iterate on queries, and write schema-aware code.
- **🔒 Privacy-first**: Your data stays local, and is only shared between your AI agent and databases through a secure MCP server.
- **🧠 Collaborative learning**: The more your agents use ToolFront, the better they remember your data. Requires API key.

<br>
<div align="center">
<img alt="diagram" src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/graph.png" width="100%">
</div>

## Quickstart

ToolFront runs on your computer through an [MCP](https://modelcontextprotocol.io/) server, a secure protocol that lets apps provide context to LLM models.

### Prerequisites

- **[uv](https://docs.astral.sh/uv/)** or **[Docker](https://www.docker.com/)** to run the MCP server (we recommend **uv**)
- **URLs** for your databases - [see below](#databases)
- **API key** (optional) for collaborative learning - [see below](#collaborative-in-context-learning)


### Run ToolFront in your AI Framework or IDE

first, create an MCP config by following the instructions for your chosen framework or IDE. 

| IDE | Setup Instructions | Install with UV | Install with Docker |
|-----|-------------------|-----------------|-------------------|
| [**Cursor**](https://docs.cursor.com/context/model-context-protocol#manual-configuration) | Settings → Cursor Settings → MCP Tools (or create `.cursor/mcp.json` file) | [🔗 Quick Install](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJ0b29sZnJvbnRbYWxsXSIsIkRBVEFCQVNFLVVSTC0xIiwiREFUQUJBU0UtVVJMLTIiLCItLWFwaS1rZXkiLCJZT1VSLUFQSS1LRVkiXX0K) | [🔗 Quick Install](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoiZG9ja2VyIiwiYXJncyI6WyJydW4iLCItaSIsImFudGlkbWcvdG9vbGZyb250IiwiREFUQUJBU0UtVVJMLTEiLCJEQVRBQkFTRS1VUkwtMiIsIi0tYXBpLWtleSIsIllPVVItQVBJLUtFWSJdfQo=) |
| [**GitHub Copilot (VSCode)**](https://docs.github.com/en/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) | Copilot icon → Edit preferences → Copilot Chat → MCP | [🔗 Quick Install](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22toolfront[all]%22%2C%22DATABASE-URL-1%22%2C%22DATABASE-URL-2%22%2C%22--api-key%22%2C%22YOUR-API-KEY%22%5D%7D) | [🔗 Quick Install](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22antidmg%2Ftoolfront%22%2C%22DATABASE-URL-1%22%2C%22DATABASE-URL-2%22%2C%22--api-key%22%2C%22YOUR-API-KEY%22%5D%7D) |


Then, edit the MCP configuration with your database connection URLs and optional API key:

<details>
<summary><strong>Edit UV Config</strong></summary>

```json
{
  "toolfront": {
    "command": "uvx",
    "args": [
      "toolfront[all]",
      "snowflake://user:pass@org",
      "postgresql://user:pass@host:port/db",
      "--api-key", "YOUR-API-KEY" // Optional
    ]
  }
}
```

</details>

<details>
<summary><strong>Edit Docker Config</strong></summary>

```json
{
  "toolfront": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "antidmg/toolfront",
      "snowflake://user:pass@org",
      "postgresql://user:pass@host:port/db",
      "--api-key", "YOUR-API-KEY" // Optional
    ]
  }
}
```

</details>
<br>

You're all set! You can now ask your AI agent about your databases.

> [!TIP]
> By default, `uvx toolfront[all]` installs all database drivers. To keep things lighter, you can install only the ones you need e.g. `uvx toolfront[postgres,mysql]`. See [Databases](#databases) for the full list of drivers.

### Run ToolFront in your Terminal

You can also run ToolFront directly with SSE from your terminal by using one of the following commands. Remember to replace the placeholder database URLs and API key with your own:

```bash
# Using uvx
uvx "toolfront[snowflake,postgres]" "snowflake://user:pass@org" "postgres://user:pass@host:port/db" --api-key "YOUR-API-KEY"

# Using Docker  
docker run -i antidmg/toolfront "snowflake://user:pass@org" "postgres://user:pass@host:port/db" --api-key "YOUR-API-KEY"
```

> [!TIP]
> **Version control**: You can pin to specific versions for consistency. Use `toolfront==0.1.x` for UV or `antidmg/toolfront:0.1.x` for Docker.


## Collaborative In-context Learning

Data teams keep rewriting the same queries because past work often gets siloed, scattered, or lost. ToolFront teaches AI agents how your team works with your databases through [in-context learning](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html#in-context-learning-key-concept). With ToolFront, your agents can:

- Reason about historical query patterns
- Remember relevant tables and schemas
- Reference your and your teammates' work

```
User A — Agent A ──┐
                   ├── shared database context ← ToolFront
User B — Agent B ──┤
                   │
User C — Agent C ──┘
```

> [!NOTE]
> In-context learning is currently in open beta. To request an API key, please email Esteban at [esteban@kruskal.ai](mailto:esteban@kruskal.ai) or hop into our [Discord server](https://discord.gg/rRyM7zkZTf).


## Databases

ToolFront supports the following databases. The table below lists the required extra name for installation (e.g., `uvx "toolfront[extra-name]"`), the connection URL format, and links to official documentation.

| Database | Driver Name | URL Format |
|----------|------------|------------|
| BigQuery | `bigquery` | `bigquery://{project-id}?credentials_path={path-to-credentials.json}` | [Google Cloud Docs](https://cloud.google.com/bigquery/docs/authentication) |
| Databricks | `databricks` | `databricks://token:{token}@{workspace}.cloud.databricks.com/{catalog}?http_path={warehouse-path}` | [Databricks Docs](https://docs.databricks.com/integrations/jdbc-odbc-bi.html#get-connection-details) |
| DuckDB | `