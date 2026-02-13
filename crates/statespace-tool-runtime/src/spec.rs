//! Tool specification parsing and validation.
//!
//! ```yaml
//! tools:
//!   - [ls]                                 # Simple command, extra args allowed
//!   - [cat, { }]                           # Placeholder accepts any value
//!   - [cat, { regex: ".*\\.md$" }]         # Regex-constrained placeholder
//!   - [psql, -c, { regex: "^SELECT" }, ;]  # Trailing ; disables extra args
//! ```

use regex::Regex;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ToolPart {
    Literal(String),
    Placeholder { regex: Option<CompiledRegex> },
}

#[derive(Debug, Clone)]
pub struct CompiledRegex {
    pub pattern: String,
    pub regex: Regex,
}

impl PartialEq for CompiledRegex {
    fn eq(&self, other: &Self) -> bool {
        self.pattern == other.pattern
    }
}

impl Eq for CompiledRegex {}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ToolSpec {
    pub parts: Vec<ToolPart>,
    pub options_disabled: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
#[non_exhaustive]
pub enum SpecError {
    #[error("invalid regex pattern '{pattern}': {message}")]
    InvalidRegex { pattern: String, message: String },
    #[error("empty tool specification")]
    EmptySpec,
    #[error("invalid tool part: {0}")]
    InvalidPart(String),
}

pub type SpecResult<T> = Result<T, SpecError>;

impl ToolSpec {
    /// # Errors
    ///
    /// Returns `SpecError` when the tool specification is empty or invalid.
    pub fn parse(raw: &[serde_json::Value]) -> SpecResult<Self> {
        if raw.is_empty() {
            return Err(SpecError::EmptySpec);
        }

        let options_disabled = raw.last().is_some_and(|v| v.as_str() == Some(";"));

        let parts = raw
            .iter()
            .filter(|v| v.as_str() != Some(";"))
            .map(Self::parse_part)
            .collect::<SpecResult<Vec<_>>>()?;

        if parts.is_empty() {
            return Err(SpecError::EmptySpec);
        }

        Ok(Self {
            parts,
            options_disabled,
        })
    }

    fn parse_part(value: &serde_json::Value) -> SpecResult<ToolPart> {
        match value {
            serde_json::Value::String(s) => Ok(ToolPart::Literal(s.clone())),

            serde_json::Value::Object(obj) => {
                if obj.is_empty() {
                    return Ok(ToolPart::Placeholder { regex: None });
                }

                if let Some(pattern) = obj.get("regex").and_then(|v| v.as_str()) {
                    let regex = Regex::new(pattern).map_err(|e| SpecError::InvalidRegex {
                        pattern: pattern.to_string(),
                        message: e.to_string(),
                    })?;
                    return Ok(ToolPart::Placeholder {
                        regex: Some(CompiledRegex {
                            pattern: pattern.to_string(),
                            regex,
                        }),
                    });
                }

                Err(SpecError::InvalidPart(format!(
                    "unknown object keys: {:?}",
                    obj.keys().collect::<Vec<_>>()
                )))
            }

            _ => Err(SpecError::InvalidPart(format!(
                "expected string or object, got: {value}"
            ))),
        }
    }
}

#[must_use]
pub fn is_valid_tool_call(command: &[String], specs: &[ToolSpec]) -> bool {
    if command.is_empty() {
        return false;
    }
    specs.iter().any(|spec| matches_spec(command, spec))
}

fn matches_spec(command: &[String], spec: &ToolSpec) -> bool {
    if command.len() < spec.parts.len() {
        return false;
    }

    if command.len() > spec.parts.len() && spec.options_disabled {
        return false;
    }

    for (i, part) in spec.parts.iter().enumerate() {
        let cmd_part = &command[i];

        match part {
            ToolPart::Literal(lit) => {
                if cmd_part != lit {
                    return false;
                }
            }
            ToolPart::Placeholder { regex: None } => {}
            ToolPart::Placeholder {
                regex: Some(compiled),
            } => {
                if !compiled.regex.is_match(cmd_part) {
                    return false;
                }
            }
        }
    }

    true
}

#[cfg(test)]
#[allow(clippy::unwrap_used)]
mod tests {
    use super::*;

    fn make_spec(parts: Vec<ToolPart>, options_disabled: bool) -> ToolSpec {
        ToolSpec {
            parts,
            options_disabled,
        }
    }

    fn lit(s: &str) -> ToolPart {
        ToolPart::Literal(s.to_string())
    }

    fn placeholder() -> ToolPart {
        ToolPart::Placeholder { regex: None }
    }

    fn regex_placeholder(pattern: &str) -> ToolPart {
        ToolPart::Placeholder {
            regex: Some(CompiledRegex {
                pattern: pattern.to_string(),
                regex: Regex::new(pattern).unwrap(),
            }),
        }
    }

    #[test]
    fn validate_simple_match() {
        let specs = vec![make_spec(vec![lit("ls")], false)];
        assert!(is_valid_tool_call(&["ls".to_string()], &specs));
    }

    #[test]
    fn validate_with_extra_args_allowed() {
        let specs = vec![make_spec(vec![lit("ls")], false)];
        assert!(is_valid_tool_call(
            &["ls".to_string(), "-la".to_string()],
            &specs
        ));
    }

    #[test]
    fn validate_with_extra_args_disabled() {
        let specs = vec![make_spec(vec![lit("ls")], true)];
        assert!(!is_valid_tool_call(
            &["ls".to_string(), "-la".to_string()],
            &specs
        ));
    }

    #[test]
    fn validate_placeholder_matches_any() {
        let specs = vec![make_spec(vec![lit("cat"), placeholder()], false)];

        assert!(is_valid_tool_call(
            &["cat".to_string(), "file.txt".to_string()],
            &specs
        ));
        assert!(is_valid_tool_call(
            &["cat".to_string(), "anything".to_string()],
            &specs
        ));
    }

    #[test]
    fn validate_regex_placeholder() {
        let specs = vec![make_spec(
            vec![lit("cat"), regex_placeholder(r".*\.md$")],
            false,
        )];

        assert!(is_valid_tool_call(
            &["cat".to_string(), "README.md".to_string()],
            &specs
        ));
        assert!(!is_valid_tool_call(
            &["cat".to_string(), "README.txt".to_string()],
            &specs
        ));
    }

    #[test]
    fn validate_regex_with_options_disabled() {
        let specs = vec![make_spec(
            vec![lit("cat"), regex_placeholder(r".*\.md$")],
            true,
        )];

        assert!(is_valid_tool_call(
            &["cat".to_string(), "file.md".to_string()],
            &specs
        ));

        assert!(!is_valid_tool_call(
            &["cat".to_string(), "file.md".to_string(), "-n".to_string()],
            &specs
        ));

        assert!(!is_valid_tool_call(
            &["cat".to_string(), "file.txt".to_string()],
            &specs
        ));
    }

    #[test]
    fn validate_complex_psql_spec() {
        let specs = vec![make_spec(
            vec![lit("psql"), lit("-c"), regex_placeholder("^SELECT")],
            true,
        )];

        assert!(is_valid_tool_call(
            &[
                "psql".to_string(),
                "-c".to_string(),
                "SELECT * FROM users".to_string()
            ],
            &specs
        ));

        assert!(!is_valid_tool_call(
            &[
                "psql".to_string(),
                "-c".to_string(),
                "INSERT INTO users VALUES (1)".to_string()
            ],
            &specs
        ));

        assert!(!is_valid_tool_call(
            &[
                "psql".to_string(),
                "-c".to_string(),
                "SELECT 1".to_string(),
                "--extra".to_string()
            ],
            &specs
        ));
    }

    #[test]
    fn validate_empty_command() {
        let specs = vec![make_spec(vec![lit("ls")], false)];
        assert!(!is_valid_tool_call(&[], &specs));
    }

    #[test]
    fn validate_placeholder_is_required() {
        let specs = vec![make_spec(vec![lit("ls"), placeholder()], false)];

        assert!(!is_valid_tool_call(&["ls".into()], &specs));
        assert!(is_valid_tool_call(&["ls".into(), "dir".into()], &specs));
        assert!(is_valid_tool_call(
            &["ls".into(), "dir".into(), "-la".into()],
            &specs
        ));
    }

    #[test]
    fn validate_multiple_specs() {
        let specs = vec![
            make_spec(vec![lit("ls")], false),
            make_spec(vec![lit("cat"), placeholder()], false),
        ];

        assert!(is_valid_tool_call(&["ls".to_string()], &specs));
        assert!(is_valid_tool_call(
            &["cat".to_string(), "file.txt".to_string()],
            &specs
        ));
        assert!(!is_valid_tool_call(&["rm".to_string()], &specs));
    }
}
