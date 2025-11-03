---
icon: material/apps
---

# Applications

ToolFront applications are Markdown projects that define tools and instructions for AI agents. 

Apps have two requirements:

1. A `README.md` file as the main entry point
2. Tools defined in `.md` files using YAML frontmatter

## README

Every application requires a `README.md` with general instructions and tools for your agent.

```markdown title="README.md"
---
tools:
  - [ls]
  - [cat]
  - [tree]

---

# My Application

You are an analyst.
Use `ls`, `cat`, and `tree` to explore project files.
```

## Tools

Tools let agents execute commands to interact with your project's directory or external systems.

```markdown title="page.md"
---
tools:
  - [ls]                                              # File navigation
  - [cat]                                             # Read files
  - [grep, -r]                                        # Search content
  - [curl, -X, GET]                                   # HTTP requests
  - [python3, scripts/analyze.py]                     # Custom scripts
  - [psql, -U, $USER, -d, $DATABASE, -c, {query}]     # Database queries

---

# Data Analysis App

Use the provided tools to answer the user's question

## Available Tools

- `ls` and `cat` - Navigate and read project files
- `grep` - Search through documents in `/data/`
- `curl` - Make HTTP requests to external APIs
- `psql` - Query the PostgreSQL database
- `analyze.py` - Run custom data analysis scripts
```


There are three ways to pass variables to tools:

=== ":material-code-braces:{ .middle } &nbsp; `{parameters}`"

    ```markdown
    ---
    tools:
      - [curl, "https://api.com/products/{product_id}"]
    ---

    Call the tools to ...
    ```

    Use curly braces to define placeholders that agents will fill with specific values:

    ```bash
    Calling "curl https://api.com/products/prod-123"
    ```


=== ":material-flag:{ .middle } &nbsp; `--arguments`"

    ```markdown
    ---
    tools:
      - [gh, issue, create]
    ---

    Call the tools to ...
    ```

    Declare base commands that agents can extend with their own arguments, flags, and options.

    ```bash
    Calling "gh issue create --title 'Bug report' --repo owner/repo"
    ```    

=== ":material-variable:{ .middle } &nbsp; `$ENV_VARIABLES`"

    ```markdown
    ---
    tools:
      - [stripe, products, list, --api-key, $STRIPE_KEY]
    ---

    Call the tools to ...
    ```

    Reference environment variables (preceded by `$`) to pass sensitive data to tools.

    ```bash
    Calling "stripe products list --api-key sk_fake_placeholder_key"
    ```

!!! tip "Learning Tools"
    Agents can learn how to use tools by passing the `--help` flag.

## Project structure

Organize your application however makes sense for your use case. For example:

```
my-app/
├── README.md           # Required: main entry point
├── src/
│   ├── api.md          # API-related tools
│   ├── search.md       # Search functionality
│   └── database.md     # Database tools
├── data/
│   ├── documents.csv   # Data files agents can read
│   └── reports.json
├── scripts/
│   └── analyze.py      # Custom tool scripts
└── config.yaml         # Configuration files
```


## Running Locally

Run your application on your local machine

```bash
toolfront run ./my-app
# Returns: http://127.0.0.1:8000
```

Once running, interact with it using the [Python SDK](./python_sdk.md) or [MCP Server](./mcp_server.md).

!!! toolfront "Deploy your Apps 🔥"

    Deploy your application to get a shareable URL.

    ```bash
    toolfront deploy ./my-app
    ```

    Choose from three deployment options:

    === ":material-web: Community Cloud (Free)"

        Perfect for personal projects and experimentation. Deploy up to 5 public applications, completely free.

        ```bash
        toolfront deploy ./my-app
        # Returns: https://cloud.statespace.com/you/my-app
        ```

    === ":material-account-group: Statespace Cloud (Pro)"

        For teams and production use. Deploy up to 20 public or private applications with authentication.

        ```bash
        toolfront deploy ./my-app --private
        # Returns: https://cloud.statespace.com/team/my-app
        ```

    === ":material-lock: Self-Hosted (Enterprise)"

        For enterprise deployments. Run unlimited applications on your own infrastructure using Docker or KBs.

        ```bash
        # Coming soon!
        ```

    Once deployed, interact with your application using the Python SDK or MCP server:

    === ":simple-python: &nbsp; Python SDK"

        ```python
        from toolfront import Application

        app = Application(
            "https://cloud.statespace.com/team/my-app",
            params={"API_KEY": "your-api-key"} # Optiona: only for private apps
        )

        result = app.run("Your prompt", model="openai:gpt-5")
        ```
 

    === ":simple-modelcontextprotocol: &nbsp; MCP Server"

        ```json
        {
          "mcpServers": {
            "my-app": {
              "command": "uvx",
              "args": ["toolfront", "mcp", "https://cloud.statespace.com/you/my-app"]
            }
          }
        }
        ```

    [Sign up for free](https://cloud.statespace.com/signup){ .md-button .md-button--primary }
