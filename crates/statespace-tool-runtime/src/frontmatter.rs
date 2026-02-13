//! Frontmatter parsing for YAML (`---`) and TOML (`+++`) formats.

use crate::error::Error;
use crate::spec::ToolSpec;
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
struct RawFrontmatter {
    #[serde(default)]
    tools: Vec<Vec<serde_json::Value>>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Frontmatter {
    pub specs: Vec<ToolSpec>,
    pub tools: Vec<Vec<String>>,
}

impl Frontmatter {
    #[must_use]
    pub fn has_tool(&self, command: &[String]) -> bool {
        if command.is_empty() {
            return false;
        }

        self.tools.iter().any(|tool| {
            if tool.is_empty() {
                return false;
            }

            if command.len() != tool.len() {
                return false;
            }

            if tool[0] != command[0] {
                return false;
            }

            true
        })
    }

    #[must_use]
    pub fn tool_names(&self) -> Vec<&str> {
        self.tools
            .iter()
            .filter_map(|tool| tool.first().map(String::as_str))
            .collect()
    }
}

/// # Errors
///
/// Returns errors when frontmatter is missing or malformed.
pub fn parse_frontmatter(content: &str) -> Result<Frontmatter, Error> {
    if let Some(yaml_content) = extract_yaml_frontmatter(content) {
        return parse_yaml(&yaml_content);
    }

    if let Some(toml_content) = extract_toml_frontmatter(content) {
        return parse_toml(&toml_content);
    }

    Err(Error::NoFrontmatter)
}

fn convert_raw(raw: &RawFrontmatter) -> Result<Frontmatter, Error> {
    let mut specs = Vec::new();
    let mut tools = Vec::new();

    for tool_parts in &raw.tools {
        match ToolSpec::parse(tool_parts) {
            Ok(spec) => specs.push(spec),
            Err(e) => {
                return Err(Error::FrontmatterParse(format!("Invalid tool spec: {e}")));
            }
        }

        let legacy: Vec<String> = tool_parts
            .iter()
            .filter_map(|v| match v {
                serde_json::Value::String(s) if s != ";" => Some(s.clone()),
                _ => None,
            })
            .collect();
        if !legacy.is_empty() {
            tools.push(legacy);
        }
    }

    Ok(Frontmatter { specs, tools })
}

fn extract_yaml_frontmatter(content: &str) -> Option<String> {
    let trimmed = content.trim_start();

    if !trimmed.starts_with("---") {
        return None;
    }

    let after_open = &trimmed[3..];
    let close_pos = after_open.find("\n---")?;

    Some(after_open[..close_pos].trim().to_string())
}

fn extract_toml_frontmatter(content: &str) -> Option<String> {
    let trimmed = content.trim_start();

    if !trimmed.starts_with("+++") {
        return None;
    }

    let after_open = &trimmed[3..];
    let close_pos = after_open.find("\n+++")?;

    Some(after_open[..close_pos].trim().to_string())
}

fn parse_yaml(content: &str) -> Result<Frontmatter, Error> {
    let raw: RawFrontmatter = serde_yaml::from_str(content)
        .map_err(|e| Error::FrontmatterParse(format!("YAML parse error: {e}")))?;
    convert_raw(&raw)
}

fn parse_toml(content: &str) -> Result<Frontmatter, Error> {
    let raw: RawFrontmatter = toml::from_str(content)
        .map_err(|e| Error::FrontmatterParse(format!("TOML parse error: {e}")))?;
    convert_raw(&raw)
}

#[cfg(test)]
#[allow(clippy::unwrap_used)]
mod tests {
    use super::*;
    use crate::spec::is_valid_tool_call;

    fn legacy_frontmatter(tools: Vec<Vec<String>>) -> Frontmatter {
        Frontmatter {
            specs: vec![],
            tools,
        }
    }

    #[test]
    fn test_parse_yaml_frontmatter() {
        let markdown = r#"---
tools:
  - ["ls", "{path}"]
  - ["cat", "{path}"]
---

# Documentation
"#;

        let fm = parse_frontmatter(markdown).unwrap();
        assert_eq!(fm.tools.len(), 2);
        assert_eq!(fm.tools[0], vec!["ls", "{path}"]);
        assert_eq!(fm.tools[1], vec!["cat", "{path}"]);
        assert_eq!(fm.specs.len(), 2);
    }

    #[test]
    fn test_parse_toml_frontmatter() {
        let markdown = r#"+++
tools = [
  ["ls", "{path}"],
  ["cat", "{path}"],
]
+++

# Documentation
"#;

        let fm = parse_frontmatter(markdown).unwrap();
        assert_eq!(fm.tools.len(), 2);
        assert_eq!(fm.tools[0], vec!["ls", "{path}"]);
    }

    #[test]
    fn test_no_frontmatter() {
        let markdown = "# Just a regular markdown file";
        let result = parse_frontmatter(markdown);
        assert!(matches!(result, Err(Error::NoFrontmatter)));
    }

    #[test]
    fn test_has_tool() {
        let fm = legacy_frontmatter(vec![
            vec!["ls".to_string(), "{path}".to_string()],
            vec!["cat".to_string(), "{path}".to_string()],
            vec!["search".to_string()],
        ]);

        assert!(fm.has_tool(&["search".to_string()]));
        assert!(fm.has_tool(&["ls".to_string(), "docs/".to_string()]));
        assert!(fm.has_tool(&["cat".to_string(), "index.md".to_string()]));
        assert!(!fm.has_tool(&["grep".to_string(), "pattern".to_string()]));
        assert!(!fm.has_tool(&[]));
    }

    #[test]
    fn test_tool_names() {
        let fm = legacy_frontmatter(vec![
            vec!["ls".to_string()],
            vec!["cat".to_string()],
            vec!["search".to_string()],
        ]);

        let names = fm.tool_names();
        assert_eq!(names, vec!["ls", "cat", "search"]);
    }

    #[test]
    fn test_e2e_regex_constraint() {
        let markdown = r#"---
tools:
  - [psql, -c, { regex: "^SELECT" }, ";"]
---
"#;

        let fm = parse_frontmatter(markdown).unwrap();

        assert!(is_valid_tool_call(
            &[
                "psql".to_string(),
                "-c".to_string(),
                "SELECT * FROM users".to_string()
            ],
            &fm.specs
        ));

        assert!(!is_valid_tool_call(
            &[
                "psql".to_string(),
                "-c".to_string(),
                "INSERT INTO users VALUES (1)".to_string()
            ],
            &fm.specs
        ));

        assert!(!is_valid_tool_call(
            &[
                "psql".to_string(),
                "-c".to_string(),
                "SELECT 1".to_string(),
                "--extra".to_string()
            ],
            &fm.specs
        ));
    }

    #[test]
    fn test_e2e_options_control() {
        let markdown = r#"---
tools:
  - [ls]
  - [cat, { }, ";"]
---
"#;

        let fm = parse_frontmatter(markdown).unwrap();

        assert!(is_valid_tool_call(&["ls".to_string()], &fm.specs));
        assert!(is_valid_tool_call(
            &["ls".to_string(), "-la".to_string()],
            &fm.specs
        ));
        assert!(is_valid_tool_call(
            &["ls".to_string(), "-la".to_string(), "docs/".to_string()],
            &fm.specs
        ));

        assert!(is_valid_tool_call(
            &["cat".to_string(), "file.txt".to_string()],
            &fm.specs
        ));
        assert!(!is_valid_tool_call(
            &["cat".to_string(), "file.txt".to_string(), "-n".to_string()],
            &fm.specs
        ));
    }
}
