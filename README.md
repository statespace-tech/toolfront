<p align="center">
  <a>
    <img src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/logo.png" width="150" alt="ToolFront Logo">
  </a>
</p>

<div align="center">

# ToolFront

[![Test Suite](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml/badge.svg)](https://github.com/kruskal-labs/toolfront/actions/workflows/test.yml)
[![Discord](https://img.shields.io/discord/1323415085011701870?label=Discord&logo=discord&logoColor=white&style=flat-square)](https://discord.gg/rRyM7zkZTf)
[![X](https://img.shields.io/badge/ToolFront-black?style=flat-square&logo=x&logoColor=white)](https://x.com/toolfront)

</div>

<div align="center">

<br>

## The missing link between AI and big data

</div>

> It's hard to ask AI about your data. Out-of-the-box models struggle to understand large databases, APIs, and documents, while fine-tuned models are expensive and brittle. ToolFront solves this by helping AI models discover and learn about your data on the fly, so they can quickly answer your questions.

<br>
<div align="center">
<img alt="ToolFront diagram" src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/diagram.png" width="500">
</div>


## Features

- **🌊 Seamless**: Connect AI to all your databases, warehouses, APIs, and documents.
- **⚡ Instant**: Get up and running in seconds with a single command.
- **🧩 Pluggable**: Works with any LLM, agent framework, and IDE that supports MCP.
- **🧠 Scalable**: ToolFront automatically evaluates your AI agents and helps them improve.
- **🔒 Secure**: Your data stays local, private, and under your control.


>AI needs to be accurate and stay relevant. ToolFront’s continuous evaluation & learning (CE/CL) API automatically monitors your AI agents and improves their performance over time. This feature is in beta, and we’d love your feedback!


## Quickstart

ToolFront runs on your computer through an **[MCP server](https://modelcontextprotocol.io/)**, a secure protocol to connect apps to LLMs.

### Prerequisites

- **[uv](https://docs.astral.sh/uv/)** or **[Docker](https://www.docker.com/)** to run the MCP server (we recommend **uv**)
- **URLs** of your databases and APIs - [see below](#data-sources)
- **API key** (optional) to automatically improve your AI agents with the CE/CL API


### Run inside your AI Framework or IDE

First, create an MCP config by following the instructions for your chosen framework or IDE. 

| IDE | Setup Instructions | Install with UV | Install with Docker |
|-----|-------------------|-----------------|-------------------|
| [**Cursor**](https://docs.cursor.com/context/model-context-protocol#manual-configuration) | Settings → Cursor Settings → MCP Tools (or create `.cursor/mcp.json` file) | [🔗 Quick Install](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJ0b29sZnJvbnRbYWxsXSIsIkRBVEFCQVNFLVVSTCIsIkFQSS1VUkwiLCItLWFwaS1rZXkiLCJZT1VSLUFQSS1LRVkiXX0=) | [🔗 Quick Install](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoiZG9ja2VyIiwiYXJncyI6WyJydW4iLCItaSIsImFudGlkbWcvdG9vbGZyb250IiwiREFUQUJBU0UtVVJMIiwiQVBJLVVSTCIsIi0tYXBpLWtleSIsIllPVVItQVBJLUtFWSJdfQ==) |
| [**GitHub Copilot (VSCode)**](https://docs.github.com/en/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) | Copilot icon → Edit preferences → Copilot Chat → MCP | [🔗 Quick Install](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22toolfront%5Ball%5D%22%2C%22DATABASE-URL%22%2C%22API-URL%22%2C%22--api-key%22%2C%22YOUR-API-KEY%22%5D%7D) | [🔗 Quick Install](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22antidmg/toolfront%22%2C%22DATABASE-URL%22%2C%22API-URL%22%2C%22--api-key%22%2C%22YOUR-API-KEY%22%5D%7D) |

Then, add as many database and API URLs to the MCP configuration as you need:

<details open>
<summary><strong>Edit UV Config</strong></summary>

```json
{
  "toolfront": {
    "command": "uvx",
    "args": [
      "toolfront[all]",
      "postgresql://user:pass@host:port/db",
      "https://api.com/openapi.json?api_key=key",
      "...",
      "--api-key", "YOUR-API-KEY" // Optional: CE/CL API
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
      "postgresql://user:pass@host:port/db",
      "https://api.com/openapi.json?token=my_token",
      "--api-key", "YOUR-API-KEY" // Optional: CE/CL API
    ]
  }
}
```

</details>
<br>

You're all set! You can now ask your AI agents about your data.

> [!TIP]
> **Installation Options:** By default, `uvx toolfront[all]` installs all package extras. For a lighter setup, you can directly install the extras you need e.g. `uvx toolfront[postgres,mysql,document]`. See [Databases](#databases) and [Document Libraries](#document-libraries) for the full list of extras.

### Run directly

Spin up the ToolFront MCP server with SSE or stdio using the `--transport` flag.

```bash
# Using uvx and SSE
uvx "toolfront[postgres]" "postgres://user:pass@host:port/db" "https://api.com/spec.json?token=my_token" --transport sse

# Using Docker and stdio
docker run -i antidmg/toolfront "postgres://user:pass@host:port/db" "https://api.com/spec.json?token=my_token" --transport stdio
```

To enable self-improving AI, you can provide your CE/CL API key with the `--api-key "YOUR-API-KEY"` flag.

> [!TIP]
> **Version control**: To pin specific versions of ToolFront, use `"toolfront[all]==0.1.x"` for UV or `antidmg/toolfront:0.1.x` for Docker.

> [!TIP]
> **Localhost databases**: When connecting to localhost databases with Docker (like `duckdb` or `postgresql://user:pass@localhost:5432/db)`, add `--network HOST` before the image name. Remote databases (cloud, external servers) work without this flag.


## Data Sources

ToolFront supports databases, APIs, and document libraries:

### Databases

See the table below for the list of supported databases, extras (e.g., `uvx "toolfront[snowflake,databricks]"`) and connection URL formats.

| Database    | Extras                  | URL Format                                                                                         |
|-------------|-------------------------|----------------------------------------------------------------------------------------------------|
| BigQuery    | `bigquery`              | `bigquery://{project-id}?credentials_path={path-to-account-credentials.json}`                      |
| Databricks  | `databricks`            | `databricks://token:{token}@{workspace}.cloud.databricks.com/{catalog}?http_path={warehouse-path}` |
| DuckDB      | `duckdb`                | `duckdb://{path-to-database.duckdb}`                                                               |
| MySQL       | `mysql`                 | `mysql://{user}:{password}@{host}:{port}/{database}`                                               |
| PostgreSQL  | `postgresql`, `postgres`| `postgres://{user}:{password}@{hostname}:{port}/{database-name}`                                   |
| Snowflake   | `snowflake`             | `snowflake://{user}:{password}@{account}/{database}`                                               |
| SQL Server  | `mssql`, `sqlserver`    | `mssql://{user}:{password}@{server}:{port}/{database}`                                             |
| SQLite      | `sqlite`                | `sqlite://{path-to-database.sqlite}`                                                               |

Don't see your database? [Submit an issue](https://github.com/kruskal-labs/toolfront/issues) or pull request, or let us know in our [Discord](https://discord.gg/rRyM7zkZTf)!

> [!TIP]
> **Working with local data files?** Add `duckdb://:memory:` to your config to analyze local Parquet, CSV, Excel, and JSON files.


### APIs

ToolFronts supports virtually **all** APIs that have an [OpenAPI](https://www.openapis.org/) or [Swagger](https://swagger.io/) specification. See the table below for a list of common APIs and their specification URLs.

| API       | Specification URL                                                                                                     |
|-----------|-----------------------------------------------------------------------------------------------------------------------|
| Wikipedia | `https://en.wikipedia.org/api/rest_v1/?spec`                                                                          |
| GitHub    | `https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json`  |
| Stripe    | `https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json`                                          |
| Slack     | `https://raw.githubusercontent.com/slackapi/slack-api-specs/master/web-api/slack_web_openapi_v2.json`                 |
| Discord   | `https://raw.githubusercontent.com/discord/discord-api-spec/main/specs/openapi.json`                                  |

> [!NOTE]
> **Authentication**: For APIs that require authentication, append your API key or token to the specification URL (e.g., `https://api.com/openapi.json?token=YOUR-API-TOKEN`). ToolFront will automatically detect and use the authentication parameters in the appropriate places.

### Document Libraries

ToolFront can search and read documents from local file systems, enabling AI agents to work with unstructured data alongside databases and APIs.

| Document Types | Extras | URL Format |
|----------------|--------|------------|
| PDF, Word, PowerPoint, Excel, JSON, Markdown, TXT, XML, YAML, RTF | `document` | `file:///path/to/your/documents` |

**Usage:**
```json
{
  "toolfront": {
    "command": "uvx", 
    "args": [
      "toolfront[all]",
      "file:///path/to/your/documents",
      "postgresql://user:pass@host:port/db"
    ]
  }
}
```

## Tools

MCP tools are functions that AI agents can call to interact with external systems. ToolFront comes with tools for databases, APIs, and documents:

| Tool                | Description                                                      | Requires API Key |
|---------------------|------------------------------------------------------------------|------------------|
| `discover`          | List all configured databases, APIs, and document libraries     | ✗                |
| `search_documents`  | Search documents by name pattern or similarity                   | ✗                |
| `read_document`     | Read document contents with smart pagination                     | ✗                |
| `search_endpoints`  | Search API endpoints by pattern or similarity                    | ✗                |
| `search_tables`     | Search database tables by pattern or similarity                  | ✗                |
| `sample_table`      | Get sample rows from a database table                            | ✗                |
| `inspect_table`     | Show structure and columns of a database table                   | ✗                |
| `inspect_endpoint`  | Show structure and parameters of an API endpoint                 | ✗                |
| `query_database`    | Run read-only SQL queries against databases                      | ✗                |
| `request_api`       | Make requests to API endpoints                                   | ✗                |
| `search_queries`    | Retrieve and learn from relevant query samples                   | ✓                |
| `search_requests`   | Retrieve and learn from relevant requests samples                | ✓                |

## FAQ

<details>
<summary><strong>How is ToolFront different from other MCPs?</strong></summary>
<br>

ToolFront stands out with *multi-database* support, *self-improving* AI, and a *local-first* architecture.

**Multi-database**: Instead of being limited to a single database, ToolFront connects all your databases and APIs in one place.

**Self-improving**: ToolFront's CE/CL API monitors your AI agents and improves their performance over time

**Local-first**: Cloud solutions compromise your data and rack up egress fees. ToolFront keeps everything local.

</details>

<details>
<summary><strong>How does the CE/CL API work?</strong></summary>
<br>

The CE/CL API uses [in-context learning](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html#in-context-learning-key-concept), a novel training-free learning framework pioneered by OpenAI. By augmenting your LLM's context with relevant samples, your agents can reason by analogy over your databases and APIs to quickly arrive at the correct answer.

CE/CL requires an API key and sends your queries and request syntax to an external service. Your data and secrets always remain secure on your local system and are never transmitted.

</details>


<details>
<summary><strong>How does ToolFront keep my data safe?</strong></summary>
<br>

- **Local execution**: All database connections and queries run on machine.
- **No secrets exposure**: Database secrets are never shared with LLMs.
- **Read-only operations**: Only safe, read-only database queries are allowed.
- **No data transmission**: Your database content never leaves your environment.
- **Secure MCP protocol**: Direct communication between agents and databases without third-party storage.

</details>

<details>
<summary><strong>How do I troubleshoot connection issues?</strong></summary>
<br>

Run the `uv run toolfront[all]` or `docker run` commands with your database URLs directly from the command line. ToolFront automatically tests all connections when starting and will display detailed errors if a connection fails. If you're still having trouble, double-check your database and API URLs using the examples in the [Databases section](#data-sources) above.

</details>


## Support & Community

Need help with ToolFront? We're here to assist:

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/kruskal-labs/toolfront/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to ToolFront.

## License

ToolFront is released under the [MIT License](LICENSE). This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For the full license text, see the [LICENSE](LICENSE) file in the repository.
