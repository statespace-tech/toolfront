//! Embedded templates (AGENTS.md, favicon.svg, index.html).

pub const AGENTS_MD: &str = r#"# Statespace Application Instructions

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
"#;

pub const FAVICON_SVG: &str = r##"<?xml version="1.0" encoding="UTF-8"?>
<svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 157.32 157.32">
  <defs>
    <style>
      .cls-1 {
        fill: url(#linear-gradient);
      }
    </style>
    <linearGradient id="linear-gradient" x1="7.75" y1="91.16" x2="149.57" y2="66.16" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0a9b6e"/>
      <stop offset=".5" stop-color="#0b7"/>
      <stop offset="1" stop-color="#6ee2b3"/>
    </linearGradient>
  </defs>
  <g id="Layer_1-2" data-name="Layer 1">
    <path class="cls-1" d="M107.52.46L24.8,15.05C8.48,17.92-2.42,33.48.46,49.8l14.59,82.72c2.88,16.32,18.44,27.21,34.75,24.33l82.72-14.59c16.32-2.88,27.21-18.44,24.33-34.75l-14.59-82.72C139.4,8.48,123.84-2.42,107.52.46ZM88.04,131.84c-29.37,5.18-57.38-14.43-62.56-43.8-5.18-29.37,14.43-57.38,43.8-62.56,29.37-5.18,57.38,14.43,62.56,43.8,5.18,29.37-14.43,57.38-43.8,62.56Z"/>
  </g>
</svg>"##;

const INDEX_HTML_TEMPLATE: &str = r##"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App - Statespace</title>
    <link rel="icon" href="/favicon.svg">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fafafa; line-height: 1.6; }
        .header { background: white; border-bottom: 1px solid #e5e5e5; padding: 1rem 3rem; display: flex; align-items: center; justify-content: space-between; }
        .header-left { display: flex; align-items: center; gap: 1rem; text-decoration: none; }
        .logo { width: 32px; height: 32px; }
        .brand { font-size: 1.25rem; font-weight: 700; color: #111; }
        .github-link { display: flex; align-items: center; gap: 0.5rem; text-decoration: none; color: #666; font-size: 0.875rem; transition: color 0.15s; }
        .github-link:hover { color: #111; }
        .github-icon { width: 20px; height: 20px; }
        .container { max-width: 800px; margin: 0 auto; padding: 4rem 3rem; }
        h2 { text-align: center; color: #111; margin-bottom: 3rem; font-size: 2rem; font-weight: 600; }
        .code-block { position: relative; margin-bottom: 1.5rem; }
        .copy-btn { position: absolute; top: 0.75rem; right: 0.75rem; background: white; color: #666; border: 1px solid #ddd; padding: 0.5rem 0.75rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: all 0.15s; }
        .copy-btn:hover { background: #f9f9f9; border-color: #ccc; color: #333; }
        .copy-btn.copied { background: #0b7; border-color: #0b7; color: white; }
        pre { background: #f9f9f9; color: #333; padding: 1.5rem; padding-right: 5rem; border-radius: 6px; overflow-x: auto; margin: 0; font-size: 0.875rem; line-height: 1.6; border: 1px solid #e0e0e0; }
        code { font-family: monospace; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="header">
        <a href="https://statespace.dev" class="header-left">
            <img src="/favicon.svg" alt="Statespace" class="logo">
            <span class="brand">Statespace</span>
        </a>
        <a href="https://github.com/statespace-ai/statespace" class="github-link" target="_blank" rel="noopener">
            <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            GitHub
        </a>
    </div>
    <div class="container">
        <h2>Connect to this app</h2>
        <div class="code-block">
            <button class="copy-btn" onclick="copyCode(this, 'app-code')">Copy</button>
            <pre><code id="app-code">$ agent "tell me about this app: {current_url}"</code></pre>
        </div>
    </div>
    <div class="hidden">
{agents_md_content}
For complete instructions and available tools, check out /README
    </div>
    <script>
        function copyCode(btn, codeId) {
            const code = document.getElementById(codeId);
            navigator.clipboard.writeText(code.textContent).then(() => {
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = 'Copy';
                    btn.classList.remove('copied');
                }, 2000);
            });
        }
    </script>
</body>
</html>"##;

#[must_use]
pub fn render_index_html(base_url: &str, agents_md: &str) -> String {
    INDEX_HTML_TEMPLATE
        .replace("{current_url}", base_url)
        .replace("{agents_md_content}", agents_md)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn render_index_html_replaces_placeholders() {
        let html = render_index_html("http://localhost:8000", "# Test agents");

        assert!(html.contains("http://localhost:8000"));
        assert!(html.contains("# Test agents"));
        assert!(!html.contains("{current_url}"));
        assert!(!html.contains("{agents_md_content}"));
    }

    #[test]
    fn agents_md_contains_instructions() {
        assert!(AGENTS_MD.contains("Discover available tools"));
        assert!(AGENTS_MD.contains("Execute tools"));
    }

    #[test]
    fn favicon_is_valid_svg() {
        assert!(FAVICON_SVG.starts_with("<?xml"));
        assert!(FAVICON_SVG.contains("<svg"));
    }
}
