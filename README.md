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

> It's hard to ask AI about your data. Out-of-the-box models struggle to understand large databases and APIs, while fine-tuning models is costly and time-consuming. ToolFront solves this by helping AI models discover and learn about your data on the fly, so they can quickly answer your questions.

<br>
<div align="center">
<img alt="ToolFront diagram" src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/diagram.png" width="500">
</div>


## Features

- **🌊 Seamless**: Bring AI to all your databases, warehouses, and APIs.
- **⚡ Instant**: Get up and running in seconds with a single command.
- **🧩 Pluggable**: Works with any LLM, agent library, and IDE that supports MCP.
- **🧠 Self-improving**: Your AI learns from experience, becoming smarter and faster over time.
- **🔒 Secure**: Your data stays local, private, and under your control.


## Quickstart

ToolFront runs on your computer through an **[MCP server](https://modelcontextprotocol.io/)**, a secure protocol that lets apps provide context to LLM models.

### Prerequisites

- **[uv](https://docs.astral.sh/uv/)** or **[Docker](https://www.docker.com/)** to run the MCP server (we recommend **uv**)
- **URLs** of your databases and APIs - [see below](#data-sources)
- **API key** (optional) enables self-improving AI with the teacher API


### Run ToolFront with your AI Framework or IDE

First, create an MCP config by following the instructions for your chosen framework or IDE. 

| IDE | Setup Instructions | Install with UV | Install with Docker |
|-----|-------------------|-----------------|-------------------|
| [**Cursor**](https://docs.cursor.com/context/model-context-protocol#manual-configuration) | Settings → Cursor Settings → MCP Tools (or create `.cursor/mcp.json` file) | [🔗 Quick Install](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJ0b29sZnJvbnRbYWxsXSIsIkRBVEFCQVNFLVVSTC0xIiwiREFUQUJBU0UtVVJMLTIiLCItLWFwaS1rZXkiLCJZT1VSLUFQSS1LRVkiXX0K) | [🔗 Quick Install](https://cursor.com/install-mcp?name=toolfront&config=eyJjb21tYW5kIjoiZG9ja2VyIiwiYXJncyI6WyJydW4iLCItaSIsImFudGlkbWcvdG9vbGZyb250IiwiREFUQUJBU0UtVVJMLTEiLCJEQVRBQkFTRS1VUkwtMiIsIi0tYXBpLWtleSIsIllPVVItQVBJLUtFWSJdfQo=) |
| [**GitHub Copilot (VSCode)**](https://docs.github.com/en/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp) | Copilot icon → Edit preferences → Copilot Chat → MCP | [🔗 Quick Install](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22toolfront[all]%22%2C%22DATABASE-URL-1%22%2C%22DATABASE-URL-2%22%2C%22--api-key%22%2C%22YOUR-API-KEY%22%5D%7D) | [🔗 Quick Install](https://insiders.vscode.dev/redirect/mcp/install?name=toolfront&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22antidmg%2Ftoolfront%22%2C%22DATABASE-URL-1%22%2C%22DATABASE-URL-2%22%2C%22--api-key%22%2C%22YOUR-API-KEY%22%5D%7D) |


Then, add your databse and API urls to the MCP configuration:

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
      "--api-key", "YOUR-API-KEY" // Optional: learning API
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
      "https://api.com/openapi.json?secret=my_secret",
      "--api-key", "YOUR-API-KEY" // Optional: learning API
    ]
  }
}
```

</details>
<br>

You're all set! You can now ask your AI agent about your databases.

> [!TIP]
> By default, `uvx toolfront[all]` installs all database drivers. To keep things lighter, you can install only the ones you need e.g. `uvx toolfront[postgres,mysql]`. See [Databases](#databases) for the full list of drivers.

### Running ToolFront's MCP

You can also spin up the the ToolFront MCP server with SSE or stdio using the the `--transport` flag.

```bash
# Using uvx and SSE
uvx "toolfront[postgres]" "postgres://user:pass@host:port/db" "https://api.com/spec.json?secret=my_secret" --transport sse

# Using Docker and stdio
docker run -i antidmg/toolfront "postgres://user:pass@host:port/db" "https://api.com/spec.json?secret=my_secret" --transport stdio
```

You can also enable self-improving AI by passing your API key with the `--api-key "YOUR-API-KEY"` flag.

> [!TIP]
> **Version control**: You can pin specific versions of ToolFront for consistency. Use `"toolfront[all]==0.1.x"` for UV or `antidmg/toolfront:0.1.x` for Docker.


## Learning API

> AI agents can be frustrating. Every interaction feels like starting from scratch, while models constantly relearn what they already knew. ToolFront fixes this with a learning API for your AI, surfacing the right knowledge exactly when it’s needed so your AI can learn instantly.

The learning API uses [in-context learning](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html#in-context-learning-key-concept), a novel training-free learning framework pioneered by OpenAI. By augmenting your LLM's context with ever-growing query samples, your agents can reason by analogy over your databases and APIs to quickly arrive at the correct answer.

## Data Sources

### Databases

See the table below for the list of supported databases, drivers (e.g., `uvx "toolfront[snowflake,databricks]"`) and connection URL formats.

| Database | Driver | URL Format |
|----------|------------|------------|
| BigQuery | `bigquery` | `bigquery://{project-id}?credentials_path={path-to-account-credentials.json}` |
| Databricks | `databricks` | `databricks://token:{token}@{workspace}.cloud.databricks.com/{catalog}?http_path={warehouse-path}` |
| DuckDB | `duckdb` | `duckdb://{path-to-database.duckdb}` |
| MySQL | `mysql` | `mysql://{user}:{password}@{host}:{port}/{database}` |
| PostgreSQL | `postgresql`, `postgres` | `postgres://{user}:{password}@{hostname}:{port}/{database-name}` |
| Snowflake | `snowflake` | `snowflake://{user}:{password}@{account}/{database}` |
| SQL Server | `mssql`, `sqlserver` | `mssql://{user}:{password}@{server}:{port}/{database}` |
| SQLite | `sqlite` | `sqlite://{path-to-database.sqlite}` |

Don't see your database? [Submit an issue](https://github.com/kruskal-labs/toolfront/issues) or pull request, or let us know in our [Discord](https://discord.gg/rRyM7zkZTf)!

> [!TIP]
> **Working with local data files?** Add `duckdb://:memory:` to your config to analyze local Parquet, CSV, Excel, and JSON files.


### APIs

ToolFronts supports virtually **all** APIs that have an [OpenAPI](https://www.openapis.org/) or [Swagger](https://swagger.io/) specification. See the table below for a list of common APIs and their specification URLs.

| API | Specification URL |
|-----|------------------|
| GitHub | `https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json` |
| Stripe | `https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json` |
| Slack | `https://raw.githubusercontent.com/slackapi/slack-api-specs/master/web-api/slack_web_openapi_v2.json` |
| Discord | `https://raw.githubusercontent.com/discord/discord-api-spec/main/specs/openapi.json` |
| Twilio | `https://raw.githubusercontent.com/twilio/twilio-oai/main/spec/json/twilio_api_v2010.json` |
| Polygon.io | `https://api.polygon.io/openapi` |
| SendGrid | `https://api.sendgrid.com/v3/api_schema.json` |
| Jira | `https://developer.atlassian.com/cloud/jira/platform/swagger-v3.v3.json` |
| DocuSign | `https://raw.githubusercontent.com/docusign/OpenAPI-Specifications/master/esignature.rest.swagger-v2.1.json` |
| Zoom | `https://marketplace.zoom.us/docs/api-reference/zoom-api/openapi.json` |

> [!NOTE]
> **Authentication**: For APIs that require authentication, append your API key and any additional parameters to the specification URL e.g., `https://api.polygon.io/openapi?apiKey=YOUR-API-KEY`.

## Tools

MCP tools are functions that AI agents can call to interact with external systems. ToolFront comes with ten database tools:

| Tool                | Description                                                      | Requires API Key |
|---------------------|------------------------------------------------------------------|------------------|
| `test`              | Test connection to a database or API                             | ✗                |
| `discover`          | List all configured databases and APIs                           | ✗                |
| `inspect_table`     | Show structure and columns of a database table                   | ✗                |
| `inspect_endpoint`  | Show structure and parameters of an API endpoint                 | ✗                |
| `sample`            | Get sample rows from a database table                            | ✗                |
| `query`             | Run read-only SQL queries against databases                      | ✗                |
| `request`           | Make requests to API endpoints                                   | ✗                |
| `search_endpoints`  | Search API endpoints by pattern or similarity                    | ✗                |
| `search_tables`     | Search database tables by pattern or similarity                  | ✗                |
| `search_requests`   | Retrieve and learn from relevant historical requests             | ✓                |
| `search_queries`    | Retrieve and learn from relevant historical queries              | ✓                |

## FAQ

<details>
<summary><strong>How is ToolFront different from other MCPs?</strong></summary>
<br>

ToolFront stands out with *multi-database* support, *self-improving* AI, and a *local-first* architecture.

**Multi-database**: Instead of being limited to a single database, ToolFront connects all your databases and APIs in one place.

**Self-improving**: ToolFront learning API helps your AI agents get smarter and faster over time.

**Local-first**: Cloud solutions compromise your data and rack up egress fees. ToolFront keeps everything local.

</details>

<details>
<summary><strong>How does ToolFront's learning API work?</strong></summary>
<br>

ToolFront's learning API uses (in-context learning)[https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html#in-context-learning-key-concept], a novel training-free learning framework pioneered by OpenAI. By augmenting your LLM's context with ever-growing query samples, your agents can reason by analogy over your databases and APIs and arrive at the answer queicker.

</details>

<details>
<summary><strong>How does ToolFront keep my data safe?</strong></summary>
<br>

- **Local execution**: All database connections and queries run on your machine.
- **No secrets exposure**: Database secrets are never shared with LLMs.
- **Read-only operations**: Only safe, read-only database queries are allowed.
- **No data transmission**: Your database content never leaves your environment.
- **Secure MCP protocol**: Direct communication between agents and databases with no third-party storage.

</details>

<details>
<summary><strong>How do I troubleshoot connection issues?</strong></summary>
<br>

Run the `uv run toolfront[all]` or `docker run` commands with your database URLs directly from the command line. ToolFront automatically tests all connections before starting and shows detailed error messages if any connection fails.

If you're still having trouble, double-check your database URLs using the examples in the [Databases section](#data-sources) above.

</details>

## Support & Community

Need help with ToolFront? We're here to assist:

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/kruskal-labs/toolfront/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to ToolFront.

## License

ToolFront is released under the [MIT License](LICENSE). This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For the full license text, see the [LICENSE](LICENSE) file in the repository.