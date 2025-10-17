# Database CLI

ToolFront's built-in `database` CLI provides text-to-SQL capabilities for AI agents through  [Ibis](https://ibis-project.org/).

```markdown
---
tools:
  - [toolfront, database, $POSTGRES_URL]
---

# Database Page

Query the database for information about users, products, or transactions.
```


---

## Installation

Install ToolFront with your any of the 15+ database backends supported by [Ibis](https://ibis-project.org/).


=== ":simple-postgresql:{ .middle } &nbsp; PostgreSQL"

    ```bash
    pip install "toolfront[postgres]"
    ```

=== ":simple-mysql:{ .middle } &nbsp; MySQL"

    ```bash
    pip install "toolfront[mysql]"
    ```

=== ":simple-sqlite:{ .middle } &nbsp; SQLite"

    ```bash
    pip install "toolfront[sqlite]"
    ```

=== ":simple-snowflake:{ .middle } &nbsp; Snowflake"

    ```bash
    pip install "toolfront[snowflake]"
    ```

=== ":simple-googlebigquery:{ .middle } &nbsp; BigQuery"

    ```bash
    pip install "toolfront[bigquery]"
    ```

=== ":simple-databricks:{ .middle } &nbsp; Databricks"

    ```bash
    pip install "toolfront[databricks]"
    ```

---

## Available Commands

Agents use three sub-commands to explore and query databases:

| Command | Description | Example |
|---------|-------------|---------|
| `list-tables` | List all tables available in the database | `toolfront database $DB_URL list-tables` |
| `inspect-table` | Inspect table schema and view sample data | `toolfront database $DB_URL inspect-table users` |
| `query` | Execute read-only SQL queries | `toolfront database $DB_URL query "SELECT * FROM users LIMIT 10"` |

---

## Connection Strings

Use environment variables to keep database credentials private.

```markdown
---
tools:
  - [toolfront, database, $POSTGRES_URL]

---

# My Markdown page
...
```

Pass the environment variable to your agent:

=== ":simple-python:{ .middle } &nbsp; Python SDK"

    ```python
    from toolfront import Environment

    environment = Environment(
        url="file:///path/environment",
        env={"POSTGRES_URL": "postgresql://user:pass@localhost:5432/mydb"}
    )
    ```

=== ":simple-modelcontextprotocol:{ .middle } &nbsp; MCP Server"

    ```json
    {
      "mcpServers": {
        "toolfront": {
          "command": "uvx",
          "args": ["toolfront", "mcp", "file:///path/environment"],
          "env": {
            "POSTGRES_URL": "postgresql://user:pass@localhost:5432/mydb"
          }
        }
      }
    }
    ```

---

## Example Page

Here's an example Markdown page with database tools:

```markdown
---
tools:
  - [toolfront, database, $POSTGRES_URL]

---

# User Database

Query the database for user accounts and profile information.

## Available Tables

- `users` - User accounts with emails and registration dates
- `profiles` - User profiles with names and preferences

## Instructions

1. Use `list-tables` to see available tables
2. Use `inspect-table` to understand structure
3. Use `query` to run SQL and retrieve data
```
