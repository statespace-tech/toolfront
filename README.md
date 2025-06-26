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

<details open>
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

ToolFront supports the following databases. The table below lists the driver names for installation (e.g., `uvx "toolfront[snowflake,databricks]"`) and the corresponding connection URL formats.

| Database | Driver Name | URL Format |
|----------|------------|------------|
| BigQuery | `bigquery` | `bigquery://{project-id}?credentials_path={path-to-account-credentials.json}` |
| Databricks | `databricks` | `databricks://token:{token}@{workspace}.cloud.databricks.com/{catalog}?http_path={warehouse-path}` |
| DuckDB | `duckdb` | `duckdb://{path-to-database.duckdb}` |
| MySQL | `mysql` | `mysql://{user}:{password}@{host}:{port}/{database}` |
| PostgreSQL | `postgresql`, `postgres`, `psql` | `postgres://{user}:{password}@{hostname}:{port}/{database-name}` |
| Snowflake | `snowflake` | `snowflake://{user}:{password}@{account}/{database}` |
| SQL Server | `sqlserver` | `mssql://{user}:{password}@{server}:{port}/{database}` or `sqlserver://{user}:{password}@{server}:{port}/{database}` |
| SQLite | `sqlite` | `sqlite://{path-to-database.sqlite}` |

Don't see your database? [Submit an issue](https://github.com/kruskal-labs/toolfront/issues) or pull request, or let us know in our [Discord](https://discord.gg/rRyM7zkZTf)!

> [!TIP]
> **Working with local data files?** Add `duckdb://:memory:` to your config to analyze local Parquet, CSV, Excel, or JSON files.

## Tools

MCP tools are functions that AI agents can call to interact with external systems. ToolFront comes with seven database tools:

| Tool | Description | Requires API Key |
|------|-------------|------------------|
| `test` | Tests whether a data source connection is working | ✗ |
| `discover` | Discovers and lists all configured databases and file sources | ✗ |
| `inspect` | Inspects table schemas, showing column names, data types, and constraints | ✗ |
| `sample` | Retrieves sample rows from tables to understand data content and format | ✗ |
| `query` | Executes read-only SQL queries against databases with error handling | ✗ |
| `search_tables` | Searches for tables using regex, BM25, or Jaro-winkler similarity | ✗ |
| `search_queries` | Searches for relevant queries or tables for in-context learning | ✓ |

## FAQ

<details>
<summary><strong>How is ToolFront different from other database MCPs?</strong></summary>
<br>

ToolFront has three key advantages: **multi-database support**, **privacy-first architecture**, and **collaborative learning**.

**Multi-database support**: While some general-purpose MCP servers happen to support multiple databases, most database MCPs only work with one database at a time, forcing you to manage separate MCP servers for each connection. ToolFront connects to all your databases in one place.

**Privacy-first architecture**: Other multi-database solutions route your data through the cloud, which racks up egress fees and creates serious privacy, security, and access control issues. ToolFront keeps everything local.

**Collaborative learning**: Database MCPs just expose raw database operations. ToolFront goes further by teaching your AI agents successful query patterns from your team's work, helping them learn your specific schemas and data relationships to improve over time.

</details>

<details>
<summary><strong>How is collaborative learning different from agent memory?</strong></summary>
<br>

Agent memory stores conversation histories for individuals, whereas ToolFront's collaborative learning remembers relational query patterns across your team and databases.

When one teammate queries a database, that knowledge becomes available to other team members using ToolFront. The system gets smarter over time by learning from your team's collective database interactions.

</details>

<details>
<summary><strong>What data is collected during collaborative learning?</strong></summary>
<br>

With an API key, ToolFront only logs the query syntax and their descriptions generated by your AI agents. It never collects your actual database content or personal information. For details, see the `query` and `learn` functions in [tools.py](src/toolfront/tools.py).

</details>

<details>
<summary><strong>How does ToolFront keep my data safe?</strong></summary>
<br>

- **Local execution**: All database connections and queries run on your machine
- **No secrets exposure**: Database credentials are never shared with AI agents
- **Read-only operations**: Only safe, read-only database queries are allowed
- **No data transmission**: Your database content never leaves your environment
- **Secure MCP protocol**: Direct communication between agents and databases with no third-party storage

</details>

<details>
<summary><strong>How do I troubleshoot connection issues?</strong></summary>
<br>

Run the `uv run toolfront` or `docker run` commands with your database URLs directly from the command line. ToolFront automatically tests all connections before starting and shows detailed error messages if any connection fails.

If you're still having trouble, double-check your database URLs using the examples in the [Databases section](#databases) above.

</details>

## Support & Community

Need help with ToolFront? We're here to assist:

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/kruskal-labs/toolfront/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to ToolFront.

## License

ToolFront is released under the [MIT License](LICENSE). This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For the full license text, see the [LICENSE](LICENSE) file in the repository.