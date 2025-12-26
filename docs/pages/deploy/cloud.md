---
icon: lucide/cloud-upload
---

!!! info "First time?"

    Create a free [Statespace](https://statespace.com) account to get your API key.

# Cloud deployment

Deploy and manage applications with Statespace's CLI.

## Quick start

```console
$ toolfront app deploy ./project --private
```

## CLI usage

### `toolfront app deploy`

Deploy your application to the cloud and get a shareable URL.

**Usage:**

```bash
toolfront app deploy [OPTIONS] PATH
```

**Arguments:**

`PATH`

: Path to application repository

**Options:**

`--name`

: Custom environment name (defaults to directory name)

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--verify`

: Wait and verify environment is accessible after deployment

### `toolfront app list`

View all your deployed applications.

**Usage:**

```bash
toolfront app list [OPTIONS]
```

**Options:**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

### `toolfront app update`

Update an existing deployment with new markdown files.

**Usage:**

```bash
toolfront app update [OPTIONS] DEPLOYMENT_ID PATH
```

**Arguments:**

`DEPLOYMENT_ID`

: ID of app to update

`PATH`

: Path to application repository

**Options:**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

### `toolfront app delete`

Remove a deployment from the cloud.

**Usage:**

```bash
toolfront app delete [OPTIONS] DEPLOYMENT_ID
```

**Arguments:**

`DEPLOYMENT_ID`

: ID of app to delete

**Options:**

`--api-key`

: Gateway API key (overrides config)

`--gateway-url`

: Gateway base URL (overrides config)

`--yes, -y`

: Skip confirmation prompt