//! Error types for statespace-server
//!
//! Wraps the runtime error with HTTP-specific functionality.

use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};

// Re-export the runtime error for convenience
pub use statespace_tool_runtime::Error;
pub type Result<T> = std::result::Result<T, Error>;

/// Extension trait for HTTP status codes
pub trait ErrorExt {
    fn status_code(&self) -> StatusCode;
}

impl ErrorExt for Error {
    /// HTTP status code for this error.
    ///
    /// Security-sensitive errors (path traversal, SSRF) return 403 Forbidden
    /// rather than 404 to avoid leaking information about file existence.
    fn status_code(&self) -> StatusCode {
        match self {
            Error::InvalidCommand(_) => StatusCode::BAD_REQUEST,
            Error::CommandNotFound { .. } => StatusCode::BAD_REQUEST,
            Error::NoFrontmatter => StatusCode::BAD_REQUEST,
            Error::FrontmatterParse(_) => StatusCode::BAD_REQUEST,

            Error::PathTraversal { .. } => StatusCode::FORBIDDEN,
            Error::Security(_) => StatusCode::FORBIDDEN,

            Error::NotFound(_) => StatusCode::NOT_FOUND,
            Error::Timeout => StatusCode::REQUEST_TIMEOUT,
            Error::OutputTooLarge { .. } => StatusCode::PAYLOAD_TOO_LARGE,

            Error::Io(_) => StatusCode::INTERNAL_SERVER_ERROR,
            Error::Internal(_) => StatusCode::INTERNAL_SERVER_ERROR,
            Error::Network(_) => StatusCode::BAD_GATEWAY,

            _ => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }
}

/// Wrapper for runtime error that implements IntoResponse
#[derive(Debug)]
pub struct ServerError(pub Error);

impl From<Error> for ServerError {
    fn from(e: Error) -> Self {
        Self(e)
    }
}

impl IntoResponse for ServerError {
    fn into_response(self) -> Response {
        let status = self.0.status_code();
        let body = self.0.user_message();
        (status, body).into_response()
    }
}
