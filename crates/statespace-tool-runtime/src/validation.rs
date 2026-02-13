//! Command validation and placeholder expansion.

use crate::error::Error;
use crate::frontmatter::Frontmatter;
use crate::spec::{ToolSpec, is_valid_tool_call};
use std::collections::HashMap;

/// # Errors
///
/// Returns an error when the command is empty or not present in frontmatter.
pub fn validate_command(frontmatter: &Frontmatter, command: &[String]) -> Result<(), Error> {
    if command.is_empty() {
        return Err(Error::InvalidCommand("command cannot be empty".to_string()));
    }

    if !frontmatter.has_tool(command) {
        return Err(Error::CommandNotFound {
            command: command.join(" "),
        });
    }

    Ok(())
}

/// # Errors
///
/// Returns an error when the command is empty or does not match any spec.
pub fn validate_command_with_specs(specs: &[ToolSpec], command: &[String]) -> Result<(), Error> {
    if command.is_empty() {
        return Err(Error::InvalidCommand("command cannot be empty".to_string()));
    }

    if !is_valid_tool_call(command, specs) {
        return Err(Error::CommandNotFound {
            command: command.join(" "),
        });
    }

    Ok(())
}

#[must_use]
pub fn expand_placeholders<S: std::hash::BuildHasher>(
    command: &[String],
    args: &HashMap<String, String, S>,
) -> Vec<String> {
    command
        .iter()
        .map(|part| {
            let mut result = part.clone();

            for (key, value) in args {
                let placeholder = format!("{{{key}}}");
                result = result.replace(&placeholder, value);
            }

            result
        })
        .collect()
}

#[must_use]
pub fn expand_env_vars<S: std::hash::BuildHasher>(
    command: &[String],
    env: &HashMap<String, String, S>,
) -> Vec<String> {
    command
        .iter()
        .map(|part| {
            let mut result = part.clone();

            for (key, value) in env {
                let var = format!("${key}");
                result = result.replace(&var, value);
            }

            result
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn legacy_frontmatter(tools: Vec<Vec<String>>) -> Frontmatter {
        Frontmatter {
            specs: vec![],
            tools,
        }
    }

    #[test]
    fn test_validate_command_empty() {
        let fm = legacy_frontmatter(vec![]);
        let result = validate_command(&fm, &[]);
        assert!(matches!(result, Err(Error::InvalidCommand(_))));
    }

    #[test]
    fn test_validate_command_not_found() {
        let fm = legacy_frontmatter(vec![vec!["ls".to_string()]]);

        let result = validate_command(&fm, &["cat".to_string(), "file.md".to_string()]);
        assert!(matches!(result, Err(Error::CommandNotFound { .. })));
    }

    #[test]
    fn test_validate_command_success() {
        let fm = legacy_frontmatter(vec![
            vec!["ls".to_string(), "{path}".to_string()],
            vec!["cat".to_string(), "{path}".to_string()],
        ]);

        let result = validate_command(&fm, &["ls".to_string(), "docs/".to_string()]);
        assert!(result.is_ok());

        let result = validate_command(&fm, &["cat".to_string(), "index.md".to_string()]);
        assert!(result.is_ok());
    }

    #[test]
    fn test_expand_placeholders() {
        let command = vec![
            "curl".to_string(),
            "-X".to_string(),
            "GET".to_string(),
            "https://api.com/{endpoint}".to_string(),
        ];

        let mut args = HashMap::new();
        args.insert("endpoint".to_string(), "orders".to_string());

        let expanded = expand_placeholders(&command, &args);
        assert_eq!(
            expanded,
            vec!["curl", "-X", "GET", "https://api.com/orders"]
        );
    }

    #[test]
    fn test_expand_env_vars() {
        let command = vec![
            "curl".to_string(),
            "-H".to_string(),
            "Authorization: Bearer $API_KEY".to_string(),
        ];

        let mut env = HashMap::new();
        env.insert("API_KEY".to_string(), "secret123".to_string());

        let expanded = expand_env_vars(&command, &env);
        assert_eq!(
            expanded,
            vec!["curl", "-H", "Authorization: Bearer secret123"]
        );
    }
}
