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

    #[error(transparent)]
    Http(#[from] reqwest::Error),
}

impl Error {
    pub(crate) fn cli(msg: impl Into<String>) -> Self {
        Self::Cli(msg.into())
    }
}

#[derive(Debug, Error)]
pub(crate) enum ConfigError {
    #[error(
        "API key not found. Run `statespace auth login` or set it in the config file.\nConfig file: {config_path}"
    )]
    MissingApiKey { config_path: String },

    #[error("Invalid configuration: {0}")]
    Invalid(String),
}

#[derive(Debug, Error)]
#[allow(dead_code)]
pub(crate) enum GatewayError {
    #[error("Failed to build HTTP client: {0}")]
    ClientBuild(String),

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

    #[error("Organization ID required. Run `statespace org use` to select one.")]
    MissingOrgId,
}

impl From<reqwest::Error> for GatewayError {
    fn from(e: reqwest::Error) -> Self {
        GatewayError::Http(e.to_string())
    }
}
