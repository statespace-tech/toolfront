//! Error types for the Statespace CLI.

use std::io;
use thiserror::Error;

pub(crate) type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, Error)]
pub(crate) enum Error {
    #[error("{0}")]
    Cli(String),

    #[error(transparent)]
    Config(#[from] ConfigError),

    #[error(transparent)]
    Gateway(#[from] GatewayError),

    #[error(transparent)]
    Io(#[from] io::Error),
}

impl Error {
    pub(crate) fn cli(msg: impl Into<String>) -> Self {
        Self::Cli(msg.into())
    }
}

#[derive(Debug, Error)]
pub(crate) enum ConfigError {
    #[error("API key not found. Set STATESPACE_API_KEY or run `statespace auth login`.\nConfig file: {config_path}")]
    MissingApiKey { config_path: String },

    #[error("Invalid configuration: {0}")]
    Invalid(String),
}

#[derive(Debug, Error)]
pub(crate) enum GatewayError {
    #[error("HTTP request failed: {0}")]
    Http(String),

    #[error("API error ({status}): {message}")]
    Api { status: u16, message: String },

    #[error("Failed to parse response: {0}")]
    Parse(String),

    #[error("Authentication required. Run `statespace auth login`.")]
    Unauthorized,

    #[error("Not found: {0}")]
    NotFound(String),
}

impl From<reqwest::Error> for GatewayError {
    fn from(e: reqwest::Error) -> Self {
        GatewayError::Http(e.to_string())
    }
}
