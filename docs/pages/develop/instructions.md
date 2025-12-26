---
icon: lucide/file-text
---

# Instructions

Declare agent instructions in Markdown.

## Usage

Include instructions for AI agents in the body of Markdown files.

```yaml  title="README.md" hl_lines="8-11"
---
tools:
  - [date]
  - [ls]
  - [cat]
---

# Instructions
- Run `date` to check today's date
- Use `ls` and `cat` to discover and read other files
- Check out `./tools.md` for more workflows
```

## Best practices

- Keep general instrucitons in `README.md`
- Split domain-specific instructions into separate files for progressive disclosure
- Include links to other Markdowns to help agents navigate your app

!!! question "Learn more"
    Learn how agents can take actions and navigate your app with [CLI tools](./tools.md)