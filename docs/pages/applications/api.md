---
icon: lucide/book-marked
---

# API Reference

---

<div class="grid" markdown>

<div markdown>

<span style="border: 1px solid #00bb77; border-radius: 8px; padding: 2px 8px; color: #00bb77; font-weight: bold; font-size: 0.85em;">GET</span> **`/{path}`**

Fetch resource files from the repository.

**Path parameters**

`path` <span style="color: #e6695b;">(required)</span>

: Path to resource file in the repository

**Response Attributes**

`content` <span style="color: #888;">(string)</span>

: Raw content of the requested file

</div>

<div markdown>

**Example**
```bash
curl -X GET \
https://fte499.toolfront.app/README.md
```

**Response**
```markdown
---
tools:
  - [ls]
  - [cat]

---

# Instructions
You are a helpful assistant.
```

</div>

</div>

---

<div class="grid" markdown>

<div markdown>

<span style="border: 1px solid #00bb77; border-radius: 8px; padding: 2px 8px; color: #00bb77; font-weight: bold; font-size: 0.85em;">POST</span> **`/{path}`**

Execute a tool declared in the target file's frontmatter and return the its output.

**Path parameters**

`path` <span style="color: #e6695b;">(required)</span>

:   Path to the Markdown file with tool declaration

**Body parameters**

`tool` <span style="color: #e6695b;">(required)</span>

:   Command array matching a tool declaration in the target file's frontmatter

`args` <span style="color: #6791e0;">(optional)</span>

:   Key-value pairs for `{placeholder}` substitution in the tool command

`env` <span style="color: #6791e0;">(optional)</span>

:   Key-value pairs for `$VARIABLE` substitution in the tool command

**Response Attributes**

`stdout` <span style="color: #888;">(string)</span>

: Standard output from the executed tool command

`stderr` <span style="color: #888;">(string)</span>

: Standard error output from the executed tool command

</div>

<div markdown>

**Example**
```bash
curl -X POST \
https://fte499.toolfront.app/README.md \
-H "Content-Type: application/json" \
-d '{
    "tool": ["ls", "."]
}'
```

**Response**
```json
{
  "stdout": "README.md   src   data",
  "stderr": ""
}
```

</div>

</div>