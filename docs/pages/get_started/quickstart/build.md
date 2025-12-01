---
icon: lucide/package-open
---

# Build your first app

Build your first RAG application with vector search, text-to-SQL, and agentic RAG.

## Define project layout

Start with this directory structure:

```bash
project/
├── README.md
├── src/
│   ├── agentic_rag.md
│   ├── text2sql.md
│   └── vector_search.md
└── data/
    ├── log1.txt
    ├── log2.txt
    └── log3.txt

2 directories, 7 files
```

## Set up README

Create the `README.md` with tools to navigate other files:

```yaml title="README.md"
---
tools:
  - [ls]
  - [cat]
---

# My first application
- Use `ls` and `cat` to navigate other files
```

## Add vector search

Create a page for querying vector embeddings:

```yaml title="src/vector_search.md"
---
tools:
  - [curl, -X, POST, https://host.pinecone.io/records/namespaces/user/search]
---

# Vector search instructions:
- Query documents with your vector database API
```

> Replace the URL with your vector database API endpoint (Pinecone, Weaviate, Qdrant, etc.).

## Add text-to-SQL

Create a page for read-only database queries:

```yaml title="src/text2sql.md"
---
tools:
  - [psql, -U, $USER, -d, $DB, -c, { regex: "^SELECT\b.*" }]
---

# Text-to-SQL Instructions:
- Use `psql` for read-only PostgreSQL queries
```

> Alternatively, use your own database CLI (mysql, sqlite3, mongosh, etc.).

## Add agentic RAG

Add sample log files to `data/`:

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

Then, create a page for searching through the logs with `grep`:

```yaml title="src/agentic_rag.md"
---
tools:
  - [grep, -r, -i, { }, ../data/]
---

# Document search instructions:
- Use `grep` to search documents in `../data/`.
```

> The `{ }` placeholder requires agents to pass exactly one argument.


---

!!! success
    You've built your first RAG application.

    **Next**: [deploy your app](deploy.md)