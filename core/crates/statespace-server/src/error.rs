//! Error types with HTTP status code mapping.

use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};

pub use statespace_tool_runtime::Error;
pub type Result<T> = std::result::Result<T, Error>;

pub trait ErrorExt {
    fn status_code(&self) -> StatusCode;
}

impl ErrorExt for Error {
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
