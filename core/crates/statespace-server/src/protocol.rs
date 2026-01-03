//! Tool execution protocol types
//!
//! Compatible with the ToolFront Python serve.py protocol.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Request to execute a tool command.
///
/// Sent as POST body to any markdown file path.
#[derive(Debug, Deserialize)]
pub struct ActionRequest {
    /// The command to execute (e.g., ["ls", "-la", "docs/"])
    pub command: Vec<String>,

    /// Optional arguments for placeholder expansion
    #[serde(default)]
    pub args: HashMap<String, String>,

    /// Optional environment variables (accepted for compatibility, but isolated in execution)
    #[serde(default)]
    pub env: HashMap<String, String>,
}

impl ActionRequest {
    /// Validate the request format
    pub fn validate(&self) -> Result<(), String> {
        if self.command.is_empty() {
            return Err("command cannot be empty".to_string());
        }
        Ok(())
    }
}

/// Response from tool execution.
///
/// Mirrors subprocess output format for compatibility.
#[derive(Debug, Serialize)]
pub struct ActionResponse {
    /// Standard output from the command
    pub stdout: String,

    /// Standard error from the command
    pub stderr: String,

    /// Exit code (0 = success)
    pub returncode: i32,
}

impl ActionResponse {
    /// Create a successful response
    #[must_use]
    pub const fn success(output: String) -> Self {
        Self {
            stdout: output,
            stderr: String::new(),
            returncode: 0,
        }
    }

    /// Create an error response
    #[must_use]
    pub const fn error(message: String) -> Self {
        Self {
            stdout: String::new(),
            stderr: message,
            returncode: 1,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_action_request_validation() {
        let valid = ActionRequest {
            command: vec!["ls".to_string()],
            args: HashMap::new(),
            env: HashMap::new(),
        };
        assert!(valid.validate().is_ok());

        let invalid = ActionRequest {
            command: vec![],
            args: HashMap::new(),
            env: HashMap::new(),
        };
        assert!(invalid.validate().is_err());
    }

    #[test]
    fn test_action_response() {
        let success = ActionResponse::success("file1.md\nfile2.md".to_string());
        assert_eq!(success.returncode, 0);
        assert_eq!(success.stdout, "file1.md\nfile2.md");
        assert_eq!(success.stderr, "");

        let error = ActionResponse::error("command not found".to_string());
        assert_eq!(error.returncode, 1);
        assert_eq!(error.stdout, "");
        assert_eq!(error.stderr, "command not found");
    }
}
