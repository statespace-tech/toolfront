//! CLI error types.

use thiserror::Error;

pub(crate) type Result<T> = std::result::Result<T, Error>;

#[derive(Debug, Error)]
pub(crate) enum Error {
    #[error("{0}")]
    Config(#[from] ConfigError),

    #[error("{0}")]
    Gateway(#[from] GatewayError),

    #[error("{0}")]
    Io(#[from] std::io::Error),

    #[error("{0}")]
    Http(#[from] reqwest::Error),

    #[error("invalid address: {0}")]
    AddrParse(#[from] std::net::AddrParseError),

    #[error("{0}")]
    Runtime(#[from] statespace_tool_runtime::Error),

    #[error("{0}")]
    Cli(String),
}

#[derive(Debug, Error)]
pub(crate) enum ConfigError {
    #[allow(dead_code)]
    #[error("config file not found: {0}")]
    NotFound(std::path::PathBuf),

    #[allow(dead_code)]
    #[error("invalid config: {0}")]
    Invalid(String),

    #[error(
        "API key not configured.\n\
         Configure credentials using one of:\n  \
         1. Config file at {config_path}\n  \
         2. --api-key flag\n  \
         3. STATESPACE_API_KEY environment variable"
    )]
    MissingApiKey { config_path: String },
}

#[derive(Debug, Error)]
pub(crate) enum GatewayError {
    #[error("API request failed ({status}): {message}")]
    Api {
        status: reqwest::StatusCode,
        message: String,
    },

    #[error("failed to build HTTP client: {0}")]
    ClientBuild(String),

    #[error("organization ID required for this operation")]
    MissingOrgId,
}

impl Error {
    pub(crate) fn cli(msg: impl Into<String>) -> Self {
        Self::Cli(msg.into())
    }
}
