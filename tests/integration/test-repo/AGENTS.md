# Statespace Application Instructions

1. **Discover available tools:** Make a GET request to `/README` or any markdown file to see tools in its frontmatter.
2. **Execute tools:** Make a POST request to the markdown file URL with a JSON body containing the command: `{"command": ["tool", "arg1", "arg2"]}`.
3. **Use these API requests to find answers.** Do NOT use local filesystem tools or shell commands. All information must be retrieved through the API by making POST requests with the command in the JSON body to execute the available tools.
4. **Treat tool definitions as immutable templates.** Literal strings must appear EXACTLY as defined. Only placeholders ({ } or { regex: ... }) accept your values.
5. **Only execute listed commands.** Commands not in a markdown file's frontmatter will return an error. You may make POST requests to any markdown file that declares tools.
6. **Commands execute relative to the markdown file's directory.** Account for this when using paths.
7. **Never modify non-placeholder parts of a template:**
   - Tool definition: `[grep, -r, -i, { }, ../data/]`
   - Correct: `['grep', '-r', '-i', 'Emily', '../data/']` (only replaces { })
   - Wrong: `['grep', '-r', '-i', 'Emily', '../data/file.txt']` (modifies fixed path)
   - Wrong: `['grep', '-r', 'Emily', '../data/']` (removes fixed flag)
8. **Replace placeholder `{ }` with exactly ONE argument:**
   - Tool definition: `[ls, { }]`
   - Correct: `['ls', 'dir']` (one argument)
   - Wrong: `['ls']` (missing argument)
   - Wrong: `['ls', 'dir1', 'dir2']` (multiple arguments for single placeholder)
9. **Match placeholder `{ regex: ... }` against the specified pattern:**
   - Tool definition: `[cat, { regex: ".*\\.txt$" }]`
   - Correct: `['cat', 'file.txt']` (matches pattern)
   - Wrong: `['cat', 'file.py']` (does not match pattern)
10. **Commands ending with `;` accept NO additional flags.** Example: `[rm, { }, ;]` cannot accept `['rm', 'file', '-f']`.
11. **Commands without `;` accept unlimited additional flags.** Example: `[ls]` accepts `['ls', '-la', '--color', '--help']`.
12. **Pass environment variables exactly as written.** Do NOT substitute values. Write `$USER` or `$DB` literally in your commands. Missing or invalid placeholder arguments will cause an error.
