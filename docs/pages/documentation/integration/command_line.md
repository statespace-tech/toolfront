---
icon: lucide/terminal
---

# Command line

The ToolFront CLI provides a fast way to query applications directly from your terminal.

## Basic usage

Query a running application using the `ask` command.

```bash
toolfront ask http://127.0.0.1:8000 "What's in the project?" --model openai:gpt-5
```

## AI models

### Cloud providers

Specify your model using the `provider:model-name` format with the `--model` flag.

```bash
toolfront ask http://127.0.0.1:8000 \
  "Your question" \
  --model openai:gpt-5
```

### Default model

Set a default model using the `TOOLFRONT_MODEL` environment variable.

```bash
export TOOLFRONT_MODEL="openai:gpt-5"
```

Once set, you can omit the `--model` flag:

```bash
toolfront ask http://127.0.0.1:8000 "Your question"
```

## Authentication

Pass authentication parameters for protected applications.

```bash
toolfront ask https://cloud.statespace.com/you/my-app \
  "Your question" \
  --param "Authorization=Bearer your-token-here"
```

## Environment variables

Provide environment variables to your application's tools.

```bash
toolfront ask http://127.0.0.1:8000 \
  "Query the database" \
  --env "DATABASE_URL=postgres://localhost/mydb" \
  --env "API_KEY=secret-key"
```

!!! info "Defining environment variables"
    See the [Tools documentation](../application/tools.md#environment-variables) for how to define environment variables in your tool configurations.

## Verbose mode

View the agent's reasoning and tool calls during execution.

```bash
toolfront ask http://127.0.0.1:8000 \
  "Your question" \
  --model openai:gpt-5 \
  --verbose
```

## Command options

Available options for the `ask` command:

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `$TOOLFRONT_MODEL` | AI model using provider:model format |
| `--param` / `-p` | None | Authentication parameters (can be repeated) |
| `--env` | None | Environment variables for tools (can be repeated) |
| `--output-type` | `str` | Output format: `str` or `json` |
| `--verbose` | `false` | Show agent reasoning and tool calls |

!!! info "Full CLI reference"
    See the [CLI Commands documentation](../../reference/client_library/cli_commands.md) for complete command syntax and options.