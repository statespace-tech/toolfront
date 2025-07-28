<p align="center">
  <a href="https://github.com/kruskal-labs/toolfront">
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

</div>

> 

ToolFront helps you retrieve information from large databases, APIs, and documents with AI.

<!-- <br>
<div align="center">
<img alt="ToolFront diagram" src="https://raw.githubusercontent.com/kruskal-labs/toolfront/main/img/diagram.png" width="500">
</div>
<br> -->

## 🚀 Quickstart

### 1. Install ToolFront

```bash
pip install toolfront[postgres]
```

### 2. Setup your model provider API key

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

### 3. Ask about your data

<details open>
<summary><strong>Databases</strong></summary>
<br>

```python
from toolfront import Database

data = Database("postgresql://user:pass@localhost:5432/mydb")

response: list[int] = data.ask("What's the profit on our 5 best-sellers?", stream=True)

print(response)  # [1250, 980, 875, 720, 650]
```

</details>

<details>
<summary><strong>APIs</strong></summary>

```python
from toolfront import API

data = API("https://api.example.com/openapi.json")

answer: float = data.ask("What's AAPL's current stock price?", stream=True)

print(answer)  # 150.25
```

</details>

<details>
<summary><strong>Documents</strong></summary>

```python
from toolfront import Document

data = Document("/path/to/document.pdf")

answer: set[str] = data.ask("Who are the authors of this paper?", stream=True)

print(answer)  # {"John Doe", "Jane Smith"}
```

</details>

That's it! ToolFront returns results in the format you need.

> [!TIP]
> **Installation Options:** Install database-specific extras as needed: `pip install toolfront[postgres]` for PostgreSQL, `pip install toolfront[snowflake]` for Snowflake, etc. See [data sources](#data-sources) for the complete list.

## 📁 Examples

Explore complete workflows in the [`examples/`](examples/) directory:

- **[Basic Database Query](examples/basic.py)** - Simple natural language SQL
- **[Large Dataset Export](examples/large_dataset_export.py)** - Export 50k+ rows with zero token consumption
- **[Natural Language Demo](examples/natural_language_sqlite_demo.py)** - Complete DataFrame workflow example
- **[PDF Invoice Extraction](examples/pdf_extraction.py)** - Extract structured data from documents  
- **[Complete Invoice Workflow](examples/invoice_processing_workflow.py)** - Production-ready batch processing pipeline

[→ See all examples with setup instructions](examples/)

## 🤖 AI Model Configuration

ToolFront is model-agnostic and supports all major LLM providers.

<details>
<summary><strong>OpenAI</strong></summary>

Set `export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>`, then run:

```python
data.ask(..., model='openai:gpt-4o', stream=True)
```

</details>

<details>
<summary><strong>Anthropic</strong></summary>
<br>

Set `export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>`, then run:

```python
data.ask(..., model='anthropic:claude-3-5-sonnet-latest', stream=True)
```

</details>

<details>
<summary><strong>Google Gemini</strong></summary>
<br>

Set `export GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>`, then run:

```python
data.ask(..., model='google:gemini-1.5-pro', stream=True)
```

</details>

<details>
<summary><strong>Groq</strong></summary>
<br>

Set `export GROQ_API_KEY=<YOUR_GROQ_API_KEY>`, then run:

```python
data.ask(..., model='groq:llama-3.1-70b-versatile', stream=True)
```

</details>

<details>
<summary><strong>Cohere</strong></summary>
<br>

Set `export COHERE_API_KEY=<YOUR_COHERE_API_KEY>`, then run:

```python
data.ask(..., model='cohere:command-r-plus', stream=True)
```

</details>

<details>
<summary><strong>Mistral</strong></summary>
<br>

Set `export MISTRAL_API_KEY=<YOUR_MISTRAL_API_KEY>`, then run:

```python
data.ask(..., model='mistral:mistral-large-latest', stream=True)
```

</details>

<details>
<summary><strong>GROK (xAI)</strong></summary>
<br>

Set `export XAI_API_KEY=<YOUR_XAI_API_KEY>`, then run:

```python
data.ask(..., model='xai:grok-beta', stream=True)
```

</details>

<details>
<summary><strong>DeepSeek</strong></summary>
<br>

Set `export DEEPSEEK_API_KEY=<YOUR_DEEPSEEK_API_KEY>`, then run:

```python
data.ask(..., model='deepseek:deepseek-chat', stream=True)
```

</details>

<br>

You can also provide additional business context to help AI understand your data:

```python
context = "Our company sells electronics. Revenue is tracked in the 'sales' table."

data.ask("What's our best performing product category?", context=context, stream=True)
```

> [!TIP]
> ToolFront's is built atop Pydantic-AI. Check out [Pydantic-AI](https://ai.pydantic.dev/models/) for the full list of supported models and providers.

## 🧩 Structured Outputs

Type annotations automatically structure ToolFront's responses. Add annotations for structured data, or leave untyped for strings:

**Primitive types** for simple values:

```python
total_revenue: int = data.ask("What's our total revenue this month?", stream=True)
# Output: 125000

has_pending_orders: bool = data.ask("Do we have any pending orders?", stream=True)
# Output: True
```

**Pydantic objects** for structured, validated data:

```python
from pydantic import BaseModel

class Customer(BaseModel):
    name: str
    revenue: int

customers: Customer = data.ask("Who's our fastest grpwomg customer?", stream=True)
# Output:
# Customer(name='TechCorp Inc.', revenue=50000)
```

**DataFrames** for raw data exports (bypasses LLM token limits):

```python
# Using pd.DataFrame type hint returns raw data instead of LLM summary
sales: pd.DataFrame = data.ask("Get all sales transactions", stream=True)

# Result: Raw DataFrame with potentially 50k+ rows (zero additional tokens!)
sales.to_csv("export.csv")         # Export any size dataset
sales.to_excel("report.xlsx")      # All exports consume zero tokens
filtered = sales[sales > 1000]     # Process data locally for free
```

**Union types** for flexible responses:

```python
price: int | float | None = data.ask("What's the price of our best-seller?", stream=True)
# Output: 29.99
```

**Collections** for lists, dicts, and other data structures:

```python
from pydantic import BaseModel

class Car(BaseModel):
    make: str
    model: str
    year: int

inventory: list[Car] = data.ask("Show me our car inventory", stream=True)
# Output:
# [Car(make='Toyota', model='Camry', year=2023), Car(make='Honda', model='Civic', year=2024)]
```

> [!NOTE]
> If `ask()` fails to answer a question, it will return `None` when the return type annotation includes `None` (e.g. `str | None`), or raise an exception otherwise.

## 💾 Data Sources

ToolFront supports databases, APIs, and document libraries.

### Databases

The list below includes package extras, connection URLs, and parameters for all databases.

<details>
<summary><strong>Amazon Athena</strong></summary>
<br>

Install with `pip install toolfront[athena]`, then run:

```python
from toolfront import Database

data = Database(url="s3://my-bucket/", **extra_params)
```

**Parameters**:
  - `url`: S3 bucket URL for Athena queries (required)
  - `workgroup`: The Athena workgroup to use
  - `region`: AWS region (e.g., us-east-1)
  - `database`: The database name
  - `s3_staging_dir`: S3 location for query results
  - `aws_access_key_id`: AWS access key ID (optional)
  - `aws_secret_access_key`: AWS secret access key (optional)
  - `aws_session_token`: AWS session token (optional)

📚 **Documentation**: [Ibis Athena Backend](https://ibis-project.org/backends/athena)

</details>

<details>
<summary><strong>BigQuery</strong></summary>
<br>

Install with `pip install toolfront[bigquery]`, then run:

```python
from toolfront import Database

data = Database(url="bigquery://{project_id}/{dataset_id}", **extra_params)
```

**Parameters**:
  - `url`: BigQuery connection URL with project and dataset IDs (required)
  - `project_id`: GCP project ID (optional)
  - `dataset_id`: BigQuery dataset ID
  - `credentials`: Google auth credentials (optional)
  - `application_name`: Application name for tracking (optional)
  - `auth_local_webserver`: Use local webserver for authentication (default: True)
  - `auth_external_data`: Request additional scopes for external data sources (default: False)
  - `auth_cache`: Credentials cache behavior - 'default', 'reauth', or 'none' (default: 'default')
  - `partition_column`: Custom partition column identifier (default: 'PARTITIONTIME')
  - `client`: Custom google.cloud.bigquery Client instance (optional)
  - `storage_client`: Custom BigQueryReadClient instance (optional)
  - `location`: Default location for BigQuery objects (optional)
  - `generate_job_id_prefix`: Callable to generate job ID prefixes (optional)

📚 **Documentation**: [Ibis BigQuery Backend](https://ibis-project.org/backends/bigquery)

</details>

<details>
<summary><strong>ClickHouse</strong></summary>
<br>

Install with `pip install toolfront[clickhouse]`, then run:

```python
from toolfront import Database

data = Database(url="clickhouse://{user}:{password}@{host}:{port}?secure={secure}", **extra_params)
```

**Parameters**:
  - `url`: ClickHouse connection URL with credentials and connection details (required)
  - `host`: Host name of the clickhouse server (default: 'localhost')
  - `port`: ClickHouse HTTP server's port. If not passed, the value depends on whether secure is True or False
  - `database`: Default database when executing queries (default: 'default')
  - `user`: User to authenticate with (default: 'default')
  - `password`: Password to authenticate with (default: '')
  - `client_name`: Name of client that will appear in clickhouse server logs (default: 'ibis')
  - `secure`: Whether or not to use an authenticated endpoint
  - `compression`: The kind of compression to use for requests. See https://clickhouse.com/docs/en/integrations/python#compression for more information (default: True)
  - `kwargs`: Client specific keyword arguments

📚 **Documentation**: [Ibis ClickHouse Backend](https://ibis-project.org/backends/clickhouse)

</details>

<details>
<summary><strong>Databricks</strong></summary>
<br>

Install with `pip install toolfront[databricks]`, then run:

```python
from toolfront import Database

data = Database(url="databricks://", **extra_params)
```

**Parameters**:
  - `url`: Databricks connection URL (required)
  - `server_hostname`: Databricks workspace hostname
  - `http_path`: HTTP path to the SQL warehouse
  - `access_token`: Databricks personal access token
  - `catalog`: Catalog name (optional)
  - `schema`: Schema name (default: 'default')
  - `session_configuration`: Additional session configuration parameters (optional)
  - `http_headers`: Custom HTTP headers (optional)
  - `use_cloud_fetch`: Enable cloud fetch optimization (default: False)
  - `memtable_volume`: Volume for storing temporary tables (optional)
  - `staging_allowed_local_path`: Local path allowed for staging (optional)

📚 **Documentation**: [Ibis Databricks Backend](https://ibis-project.org/backends/databricks)

</details>

<details>
<summary><strong>Druid</strong></summary>
<br>

Install with `pip install toolfront[druid]`, then run:

```python
from toolfront import Database

data = Database(url="druid://localhost:8082/druid/v2/sql", **extra_params)
```

**Parameters**:
  - `url`: Druid connection URL with hostname, port, and API path (required)
  - `host`: Hostname of the Druid server (default: 'localhost')
  - `port`: Port number of the Druid server (default: 8082)
  - `path`: API path for Druid SQL queries (default: 'druid/v2/sql')

📚 **Documentation**: [Ibis Druid Backend](https://ibis-project.org/backends/druid)

</details>

<details>
<summary><strong>DuckDB</strong></summary>
<br>

Install with `pip install toolfront[duckdb]`, then run:

```python
from toolfront import Database

data = Database(url="duckdb://database.duckdb", **extra_params)
```

**Parameters**:
  - `url`: DuckDB connection URL pointing to database file (required)
  - `database`: Path to the SQLite database file, or None for in-memory database (default: None)
  - `type_map`: Optional mapping from SQLite type names to Ibis DataTypes to override schema inference

📚 **Documentation**: [Ibis DuckDB Backend](https://ibis-project.org/backends/duckdb)

</details>

<details>
<summary><strong>MSSQL</strong></summary>
<br>

Install with `pip install toolfront[mssql]`, then run:

```python
from toolfront import Database

data = Database(url="mssql://{user}:{password}@{host}:{port}/{database}", **extra_params)
```

**Parameters**:
  - `url`: MSSQL connection URL with credentials and database details (required)
  - `host`: Address of MSSQL server to connect to (default: 'localhost')
  - `user`: Username. Leave blank to use Integrated Authentication (default: None)
  - `password`: Password. Leave blank to use Integrated Authentication (default: None)
  - `port`: Port of MSSQL server to connect to (default: 1433)
  - `database`: The MSSQL database to connect to (default: None)
  - `driver`: ODBC Driver to use. On Mac and Linux this is usually 'FreeTDS'. On Windows, it is usually one of: 'ODBC Driver 11 for SQL Server', 'ODBC Driver 13 for SQL Server', 'ODBC Driver 17 for SQL Server', or 'ODBC Driver 18 for SQL Server' (default: None)
  - `kwargs`: Additional keyword arguments to pass to PyODBC (default: {})

📚 **Documentation**: [Ibis MSSQL Backend](https://ibis-project.org/backends/mssql)

</details>

<details>
<summary><strong>MySQL</strong></summary>
<br>

Install with `pip install toolfront[mysql]`, then run:

```python
from toolfront import Database

data = Database(url="mysql://{user}:{password}@{host}:{port}/{database}", **extra_params)
```

**Parameters**:
  - `url`: MySQL connection URL with credentials and database details (required)
  - `host`: Hostname (default: 'localhost')
  - `user`: Username (default: None)
  - `password`: Password (default: None)
  - `port`: Port (default: 3306)
  - `autocommit`: Autocommit mode (default: True)
  - `kwargs`: Additional keyword arguments passed to MySQLdb.connect

📚 **Documentation**: [Ibis MySQL Backend](https://ibis-project.org/backends/mysql)

</details>

<details>
<summary><strong>Oracle</strong></summary>
<br>

Install with `pip install toolfront[oracle]`, then run:

```python
from toolfront import Database

data = Database(url="oracle://{user}:{password}@{host}:{port}/{database}", **extra_params)
```

**Parameters**:
  - `url`: Oracle connection URL with credentials and database details (required)
  - `user`: Username (required)
  - `password`: Password (required)
  - `host`: Hostname (default: 'localhost')
  - `port`: Port (default: 1521)
  - `database`: Used as an Oracle service name if provided (optional)
  - `sid`: Unique name of an Oracle Instance, used to construct a DSN if provided (optional)
  - `service_name`: Oracle service name, used to construct a DSN if provided. Only one of database and service_name should be provided (optional)
  - `dsn`: An Oracle Data Source Name. If provided, overrides all other connection arguments except username and password (optional)

📚 **Documentation**: [Ibis Oracle Backend](https://ibis-project.org/backends/oracle)

</details>

<details>
<summary><strong>PostgreSQL</strong></summary>
<br>

Install with `pip install toolfront[postgres]`, then run:

```python
from toolfront import Database

# method 1
data = Database(url="postgres://{user}:{password}@{host}:{port}/{database}", **extra_params)

# method 2
data = Database(url="postgres://{user}:{password}@{host}:{port}/{database}/{schema}", **extra_params)

# method 3
data = Database(url="postgres://{user}:{password}@{host}:{port}/{database}/{schema}?sslmode=require", **extra_params)
```

**Parameters**:
  - `url`: PostgreSQL connection URL with credentials and database details (required)
  - `host`: Hostname (default: None)
  - `user`: Username (default: None) 
  - `password`: Password (default: None)
  - `port`: Port number (default: 5432)
  - `database`: Database to connect to (default: None)
  - `schema`: PostgreSQL schema to use. If None, use the default search_path (default: None)
  - `autocommit`: Whether or not to autocommit (default: True)
  - `kwargs`: Additional keyword arguments to pass to the backend client connection

📚 **Documentation**: [Ibis PostgreSQL Backend](https://ibis-project.org/backends/postgres)

</details>

<details>
<summary><strong>Snowflake</strong></summary>
<br>

Install with `pip install toolfront[snowflake]`, then run:

```python
from toolfront import Database

data = Database(url="snowflake://{user}:{password}@{account}/{database}", **extra_params)
```

**Parameters**:
  - `url`: Snowflake connection URL with credentials and account details (required)
  - `user`: Username (required)
  - `account`: A Snowflake organization ID and user ID, separated by a hyphen (required)
  - `database`: A Snowflake database and schema, separated by a / (required)
  - `password`: Password (required if authenticator not provided)
  - `authenticator`: Authentication method (required if password not provided)
  - `create_object_udfs`: Enable object UDF extensions (default: True)
  - `kwargs`: Additional arguments passed to DBAPI connection

📚 **Documentation**: [Ibis Snowflake Backend](https://ibis-project.org/backends/snowflake)

</details>

<details>
<summary><strong>SQLite</strong></summary>
<br>

Install with `pip install toolfront[sqlite]`, then run:

```python
from toolfront import Database

# connect to an existing sqlite database
data = Database(url="sqlite://path/to/local/file", **extra_params)

# connect to an ephemeral in-memory database
data = Database(url="sqlite://", **extra_params)
```

**Parameters**:
  - `url`: SQLite connection URL pointing to database file or empty for in-memory (required)
  - `database`: Path to SQLite database file, or None for in-memory database
  - `type_map`: Optional mapping from SQLite type names to Ibis DataTypes to override schema inference

📚 **Documentation**: [Ibis SQLite Backend](https://ibis-project.org/backends/sqlite)

</details>

<details>
<summary><strong>Trino (formerly Presto)</strong></summary>
<br>

Install with `pip install toolfront[trino]`, then run:

```python
from toolfront import Database

# connect using default user, password, host and port
data = Database(url=f"trino:///{catalog}/{schema}", **extra_params)

# connect with explicit user, host and port
data = Database(url=f"trino://user@localhost:8080/{catalog}/{schema}", **extra_params)
```

**Parameters**:
  - `url`: Trino connection URL with catalog and schema details (required)
  - `user`: Username to connect with (default: 'user')
  - `password`: Password to connect with, mutually exclusive with auth (default: None)
  - `host`: Hostname of the Trino server (default: 'localhost')
  - `port`: Port of the Trino server (default: 8080)
  - `database`: Catalog to use on the Trino server (default: None)
  - `schema`: Schema to use on the Trino server (default: None)
  - `source`: Application name passed to Trino (default: None)
  - `timezone`: Timezone to use for the connection (default: 'UTC')
  - `auth`: Authentication method, mutually exclusive with password (default: None)
  - `kwargs`: Additional keyword arguments passed to trino.dbapi.connect API

📚 **Documentation**: [Ibis Trino Backend](https://ibis-project.org/backends/trino)

</details>

<br>

Don't see your database? [Submit an issue](https://github.com/kruskal-labs/toolfront/issues) or pull request, or let us know in our [Discord](https://discord.gg/rRyM7zkZTf)!

> [!TIP]
> **Table Filtering**: Use the `match` parameter to filter which database tables to query using regex patterns.
> 
> ```python
> # Only query tables starting with 'sales_'
> Database("postgresql://...", match="^sales_.*")
> ```

### APIs

ToolFront supports virtually **all** APIs that have an [OpenAPI](https://www.openapis.org/) or [Swagger](https://swagger.io/) specification.

```python
from toolfront import API

data = API(spec="https://api.example.com/openapi.json", **extra_params)

answer: float = data.ask("What's AAPL's current stock price?", stream=True)
```

**Parameters**:
  - `spec`: OpenAPI/Swagger specification URL, dict, or JSON/YAML file path (required)
  - `headers`: Dictionary of HTTP headers to include in all requests (optional)
  - `params`: Dictionary of query parameters to include in all requests (optional)

### Documents

ToolFront supports documents for reading various file formats including PDF, DOCX, PPTX, Excel, HTML, Markdown, TXT, JSON, XML, YAML, and RTF.

**Install options:**
```bash
# PDF processing only
pip install toolfront[document-pdf]

# Office documents (Word, PowerPoint, Excel)  
pip install toolfront[document-office]

# Cloud document intelligence
pip install toolfront[document-cloud]

# All document formats
pip install toolfront[document-all]
```

Then run:

```python
from toolfront import Document

# Read from file path
data = Document(filepath="/path/to/document.pdf")

# Or provide text content directly
data = Document(text="Your document content here")

answer: list[float] = data.ask("What are the payment amounts in this documetn?", stream=True)
```

**Parameters**:
  - `filepath`: Path to the document file (mutually exclusive with text)
  - `text`: Document content as text (mutually exclusive with filepath)

> [!TIP]
> **Installation Options:** Use `toolfront[all]` for all database support, or install specific extras using comma-separated values e.g. `toolfront[postgres,mysql,document]`.

## 🔌 Integrations

<details>
<summary><strong>🦜️🔗 LangChain & AI Frameworks</strong></summary>

<br>

ToolFront seamlessly integrates with popular AI frameworks by providing tools that can be passed directly to your custom agents.

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from toolfront import Database

# Setup ToolFront
data = Database("postgresql://user:pass@localhost:5432/mydb")

# Create LangChain agent with ToolFront tools and prompt
llm = ChatOpenAI(model="gpt-4")
tools = data.tools()
prompt = data.prompt()

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Use the agent
result = executor.invoke({"input": "What's our monthly revenue?"})
```

**Supported Frameworks**: LangChain, LlamaIndex, AutoGPT, and any framework that accepts callable Python functions as tools.

</details>

<details>
<summary><strong>🌐 Model Context Protocol (MCP)</strong></summary>

<br>

ToolFront includes a built-in **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)** server for seamless integration with MCP-compatible AI clients like Claude Desktop.

**Setup Instructions:**
1. Create an MCP configuration file
2. Add ToolFront as a server with your data source URL
3. Connect your AI client

```json
{
  "mcpServers": {
    "toolfront": {
      "command": "uvx",
      "args": ["toolfront[postgres]", "postgresql://user:pass@host:port/db"]
    }
  }
}
```

**Compatible Clients**: Claude Desktop, Cursor, and other MCP-enabled applications.

</details>

## ❓ FAQ

<details>
<summary><strong>How does ToolFront keep my data safe?</strong></summary>
<br>

- **Local execution**: All database connections and queries run on your machine.
- **No secrets exposure**: Database secrets are never shared with LLMs.
- **Read-only operations**: Only safe, read-only database queries are allowed.

</details>

## 🤝 Support & Community

Need help with ToolFront? We're here to assist:

- **Discord**: Join our [community server](https://discord.gg/rRyM7zkZTf) for real-time help and discussions
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/kruskal-labs/toolfront/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to ToolFront.

## License

ToolFront is released under the [MIT License](LICENSE). This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For the full license text, see the [LICENSE](LICENSE) file in the repository.
