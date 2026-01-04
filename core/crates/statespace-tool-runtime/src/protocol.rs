//! Tool execution request/response protocol.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Deserialize)]
pub struct ActionRequest {
    pub command: Vec<String>,
    #[serde(default)]
    pub args: HashMap<String, String>,
    #[serde(default)]
    pub env: HashMap<String, String>,
}

impl ActionRequest {
    pub fn validate(&self) -> Result<(), String> {
        if self.command.is_empty() {
            return Err("command cannot be empty".to_string());
        }
        Ok(())
    }
}

#[derive(Debug, Serialize)]
pub struct ActionResponse {
    pub stdout: String,
    pub stderr: String,
    pub returncode: i32,
}

impl ActionResponse {
    #[must_use]
    pub const fn success(output: String) -> Self {
        Self {
            stdout: output,
            stderr: String::new(),
            returncode: 0,
        }
    }

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
