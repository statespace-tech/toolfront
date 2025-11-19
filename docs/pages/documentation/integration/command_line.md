---
icon: lucide/terminal
---

# Command Line Integration

The ToolFront CLI is perfect for quick tests and deployments. No Python needed for basic use. Full commands in [Reference](../reference/commands.md).

## Quick Prototyping

Serve and query in one go:

```bash
# Serve
toolfront serve .
# http://127.0.0.1:8000

# Query (in another terminal)
toolfront ask http://127.0.0.1:8000 "What's in the project?" --model openai:gpt-4o-mini
```

- `--model`: Provider:model (default: env TOOLFRONT_MODEL).
- `--output-type str|json`: Structured CLI output.
- `--verbose`: Show agent reasoning/tools.

## Core Commands Tutorial

### Serve Locally

```bash
toolfront serve ./app --host 0.0.0.0 --port 8001
```

Hot-reloads Markdown changes. For production: Use Docker.

### Ask (Query App)

```bash
toolfront ask URL "prompt" [OPTIONS]
```

Examples:
- Basic: `toolfront ask http://127.0.0.1:8000 "List files"`
- Structured: `toolfront ask URL "Top product?" --output-type json`
- With env: `toolfront ask URL "Query DB" --env DB_URL=...`

Integrates `application.py` ask(): Fetches instructions, runs agent.

### Deploy to Cloud

```bash
toolfront deploy ./app --name "MyApp" --verify
# https://myapp.toolfront.app
```

- `--api-key`: Override config.
- `--gateway-url`: Custom cloud.
- Free: 5 public apps; Pro: Private.

List/update/delete:
```bash
toolfront list
toolfront update DEPLOY_ID ./new-app
toolfront delete DEPLOY_ID -y
```

### MCP (From CLI)

```bash
toolfront mcp URL --transport stdio
```

For IDEs—see [MCP Server Guide](../documentation/mcp_server.md).

## Tips & Troubleshooting

- **No output?** Check model key: `echo $OPENAI_API_KEY`.
- **Tool errors?** Verbose: `--verbose` shows calls (e.g., "Called ls with .").
- **Deploy fails?** Verify API key; check quotas in [Cloud API](../reference/toolfront_cloud.md).
- **Scripting?** Pipe: `echo "prompt" | toolfront ask URL`.

CLI shines for iteration: Edit Markdown → serve → ask → repeat.

> If new to agents, see [Applications](../documentation/applications.md#ai-agent-integration). Programmatic? Use [Python SDK](../documentation/python_sdk.md). Deep dive: [Commands Reference](../reference/commands.md).
