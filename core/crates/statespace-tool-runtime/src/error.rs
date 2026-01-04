//! Error types for the tool runtime.

use thiserror::Error;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, Error)]
#[non_exhaustive]
pub enum Error {
    #[error("invalid command: {0}")]
    InvalidCommand(String),

    #[error("command not found in frontmatter: {command}")]
    CommandNotFound { command: String },

    #[error("no frontmatter found in file")]
    NoFrontmatter,

    #[error("frontmatter parse error: {0}")]
    FrontmatterParse(String),

    #[error("tool execution timeout")]
    Timeout,

    #[error("output too large: {size} bytes (limit: {limit})")]
    OutputTooLarge { size: usize, limit: usize },

    #[error("path traversal attempt: tried to access {attempted} outside boundary {boundary}")]
    PathTraversal { attempted: String, boundary: String },

    #[error("file not found: {0}")]
    NotFound(String),

    #[error("security violation: {0}")]
    Security(String),

    #[error("network error: {0}")]
    Network(String),

    #[error("io error: {0}")]
    Io(#[from] std::io::Error),

    #[error("internal error: {0}")]
    Internal(String),
}

impl Error {
    #[must_use]
    pub fn user_message(&self) -> String {
        match self {
            Self::InvalidCommand(msg) => format!("Invalid command: {msg}"),
            Self::CommandNotFound { command } => {
                format!("Command '{command}' not allowed by frontmatter")
            }
            Self::NoFrontmatter => {
                "No frontmatter found. Tools must be declared in YAML/TOML frontmatter.".to_string()
            }
            Self::FrontmatterParse(msg) => format!("Frontmatter parse error: {msg}"),
            Self::Timeout => "Tool execution timeout".to_string(),
            Self::OutputTooLarge { size, limit } => {
                format!("Output too large: {size} bytes (limit: {limit} bytes)")
            }
            Self::PathTraversal { attempted, .. } => {
                format!("Access denied: cannot access '{attempted}'")
            }
            Self::NotFound(path) => format!("File not found: {path}"),
            Self::Security(msg) => format!("Security violation: {msg}"),
            Self::Network(msg) => format!("Network error: {msg}"),
            Self::Io(e) => format!("IO error: {e}"),
            Self::Internal(_) => "Internal server error".to_string(),
        }
    }
}
