---
icon: lucide/home
---

# Statespace documentation

Build and share LLM apps in pure Markdown. This site covers the CLI, app structure, and the HTTP API.

## Quickstart

Install the CLI:

```bash
curl -fsSL https://statespace.com/install.sh | bash
```

Create a minimal app:

```yaml title="README.md"
---
tools:
  - [date]
---

# Instructions
- Run `date` to check today's date
```

Serve it locally:

```console
$ statespace serve .
```

## What to read next

- [Instructions](pages/develop/instructions.md)
- [CLI tools](pages/develop/tools.md)
- [Apps](pages/develop/apps.md)
- [Cloud deployment](pages/deploy/cloud.md)
- [Self-hosting](pages/deploy/self_hosting.md)
- [Access tokens](pages/deploy/tokens.md)
- [HTTP API](pages/connect/api.md)
- [Coding agents](pages/connect/coding_agents.md)
- [Custom agents](pages/connect/custom_agents.md)

## Community

- [GitHub](https://github.com/statespace-tech/statespace)
- [Discord](https://discord.gg/rRyM7zkZTf)
