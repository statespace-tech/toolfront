---
icon: lucide/cloud-upload
---

!!! info "First time?"

    Create a free [Statespace](https://statespace.com) account to get your API key.

# Cloud deployment

Deploy and manage applications with Statespace's CLI.

## Quick start

```console
$ statespace app create ./project --visibility private
```

## CLI usage

### `statespace app create`

Deploy your application to the cloud and get a shareable URL.

**Usage:**

```bash
statespace app create [OPTIONS] PATH
```

**Arguments:**

`PATH`

: Path to application repository

**Options:**

`--name`

: Custom environment name (defaults to directory name)

`--visibility`

: Environment visibility (`public` or `private`)

`--verify`

: Wait and verify environment is accessible after deployment

### `statespace app list`

View all your deployed applications.

**Usage:**

```bash
statespace app list
```

### `statespace app sync`

Sync a directory to an existing environment (create-or-update).

**Usage:**

```bash
statespace app sync [PATH] [--name <NAME>]
```

### `statespace app delete`

Remove a deployment from the cloud.

**Usage:**

```bash
statespace app delete [OPTIONS] ENV_ID_OR_NAME
```

**Arguments:**

`ENV_ID_OR_NAME`

: Environment ID or name to delete

**Options:**

`--yes, -y`

: Skip confirmation prompt
