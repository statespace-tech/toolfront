---
tools:
  - [curl, -X, GET, https://api.toolfront.ai/health]
  - [ls, "{path}"]
  - [cat, "{path}"]
---

# Status Checker
- Use `curl` to check if the service is up
- Use `ls` to list what files are available
- Use `cat` to view the content of a file

## Usage Examples

### List files
```json
{"command": ["ls"]}
{"command": ["ls", "{path}"], "args": {"path": "docs/"}}
```

### Read a file
```json
{"command": ["cat", "{path}"], "args": {"path": "README.md"}}
```



