---
icon: lucide/package-open
---

# Build Your First App

Let's build a status checker that lets AI agents health check an API and search log files.

## Create Project Layout

Start with this folder structure:

```
app/
├── README.md       # Navigation
├── src/
│   ├── health.md   # API status
│   └── search.md   # Document RAG
└── data/           # Log files
```

## Set Up README

Add general instructions and tools.

```markdown title="README.md"
---
tools:
  - [ls]
  - [cat]

---

# My First Application

You're a helpful assistant that monitors service health.

## Guidelines
- Use `ls` to list files
- Use `cat` to read files and discover tools
```


## Add Specialized Pages

Create pages with specific tools. Start with `health.md` for service checks.

```markdown title="src/health.md"
---
tools:
  - [curl, -X, GET, "https://httpbin.org/status/200"]

---

# API Health Check
Use `curl` to check service health (returns 200 OK if healthy).
```

Then, create `search.md` for log search with `{{ }}` as a placeholder for arguments.

```markdown title="src/search.md"
---
tools:
  - [grep, -r, {{ }}, data/]

---

# Log Search
Use `grep` to search logs in `data/` (e.g., grep -r "error" data/).
```

## Add Sample Logs

Create sample log files in `/data`.

```text title="data/doc1.txt"
2025-01-15 14:23:01 INFO [api.health] GET /status/200 - 200 OK (12ms)
2025-01-15 14:23:45 INFO [api.health] Health check passed for service-1
2025-01-15 14:24:12 INFO [auth] User 'user1' authenticated successfully
```

```text title="data/doc2.txt"
2025-02-03 09:15:22 ERROR [api.handler] GET /api/users - 500 Internal Server Error
2025-02-03 09:15:22 ERROR [database] Connection timeout after 5000ms
2025-02-03 09:15:23 WARN [api.handler] Retrying failed request (attempt 1/3)
```

```text title="data/doc3.txt"
2025-02-15 16:42:10 INFO [worker] Job 'daily-backup' started
2025-02-15 16:42:11 INFO [worker] Processing 1250 records
2025-02-15 16:42:33 INFO [worker] Job 'daily-backup' completed (status: success)
```

---

!!! success
    You've built your first app app with navigation, api calls, and file search. 
    
    **Next**: [Deploy your app](deploy.md)