//! HTTP server and Axum router.

use crate::content::{ContentResolver, LocalContentResolver};
use crate::error::ErrorExt;
use crate::templates::FAVICON_SVG;
use axum::{
    Json, Router,
    extract::{Path, State},
    http::{StatusCode, header},
    response::{Html, IntoResponse, Response},
    routing::get,
};
use statespace_tool_runtime::{
    ActionRequest, ActionResponse, BuiltinTool, ExecutionLimits, ToolExecutor, expand_env_vars,
    expand_placeholders, parse_frontmatter, validate_command_with_specs,
};
use std::path::PathBuf;
use std::sync::Arc;
use tokio::fs;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;
use tracing::{info, warn};

#[derive(Debug, Clone)]
pub struct ServerConfig {
    pub content_root: PathBuf,
    pub host: String,
    pub port: u16,
    pub limits: ExecutionLimits,
}

impl ServerConfig {
    #[must_use]
    pub fn new(content_root: PathBuf) -> Self {
        Self {
            content_root,
            host: "127.0.0.1".to_string(),
            port: 8000,
            limits: ExecutionLimits::default(),
        }
    }

    #[must_use]
    pub fn with_host(mut self, host: impl Into<String>) -> Self {
        self.host = host.into();
        self
    }

    #[must_use]
    pub const fn with_port(mut self, port: u16) -> Self {
        self.port = port;
        self
    }

    #[must_use]
    pub fn with_limits(mut self, limits: ExecutionLimits) -> Self {
        self.limits = limits;
        self
    }

    #[must_use]
    pub fn socket_addr(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }

    #[must_use]
    pub fn base_url(&self) -> String {
        format!("http://{}:{}", self.host, self.port)
    }
}

#[derive(Clone)]
pub struct ServerState {
    pub content_resolver: Arc<dyn ContentResolver>,
    pub limits: ExecutionLimits,
    pub content_root: PathBuf,
}

impl std::fmt::Debug for ServerState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ServerState")
            .field("limits", &self.limits)
            .field("content_root", &self.content_root)
            .finish_non_exhaustive()
    }
}

impl ServerState {
    #[must_use]
    pub fn from_config(config: &ServerConfig) -> Self {
        Self {
            content_resolver: Arc::new(LocalContentResolver::new(config.content_root.clone())),
            limits: config.limits.clone(),
            content_root: config.content_root.clone(),
        }
    }
}

pub fn build_router(config: ServerConfig) -> Router {
    let state = ServerState::from_config(&config);

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        .route("/", get(index_handler).post(action_handler_root))
        .route("/favicon.svg", get(favicon_handler))
        .route("/favicon.ico", get(favicon_handler))
        .route("/{*path}", get(file_handler).post(action_handler))
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}

async fn index_handler(State(state): State<ServerState>) -> Response {
    let index_path = state.content_root.join("index.html");

    if index_path.is_file() {
        match fs::read_to_string(&index_path).await {
            Ok(content) => {
                return (
                    StatusCode::OK,
                    [(header::CONTENT_TYPE, "text/html; charset=utf-8")],
                    content,
                )
                    .into_response();
            }
            Err(e) => {
                warn!("Failed to read index.html: {}", e);
            }
        }
    }

    serve_markdown("", &state).await
}

async fn favicon_handler(State(state): State<ServerState>) -> Response {
    let favicon_path = state.content_root.join("favicon.svg");

    let content = if favicon_path.is_file() {
        fs::read_to_string(&favicon_path)
            .await
            .unwrap_or_else(|_| FAVICON_SVG.to_string())
    } else {
        FAVICON_SVG.to_string()
    };

    (
        StatusCode::OK,
        [(header::CONTENT_TYPE, "image/svg+xml")],
        content,
    )
        .into_response()
}

async fn file_handler(Path(path): Path<String>, State(state): State<ServerState>) -> Response {
    serve_markdown(&path, &state).await
}

async fn serve_markdown(path: &str, state: &ServerState) -> Response {
    match state.content_resolver.resolve(path).await {
        Ok(content) => Html(content).into_response(),
        Err(e) => {
            warn!("File not found: {} ({})", path, e);
            (e.status_code(), e.user_message()).into_response()
        }
    }
}

async fn action_handler_root(
    State(state): State<ServerState>,
    Json(request): Json<ActionRequest>,
) -> Response {
    execute_action("", &state, request).await
}

async fn action_handler(
    Path(path): Path<String>,
    State(state): State<ServerState>,
    Json(request): Json<ActionRequest>,
) -> Response {
    execute_action(&path, &state, request).await
}

fn error_to_action_response(e: statespace_tool_runtime::Error) -> Response {
    let status = e.status_code();
    let response = ActionResponse::error(e.user_message());
    (status, Json(response)).into_response()
}

async fn execute_action(path: &str, state: &ServerState, request: ActionRequest) -> Response {
    if let Err(msg) = request.validate() {
        return error_response(StatusCode::BAD_REQUEST, &msg);
    }

    let file_path = match state.content_resolver.resolve_path(path).await {
        Ok(p) => p,
        Err(e) => return error_to_action_response(e),
    };

    let content = match state.content_resolver.resolve(path).await {
        Ok(c) => c,
        Err(e) => return error_to_action_response(e),
    };

    let frontmatter = match parse_frontmatter(&content) {
        Ok(fm) => fm,
        Err(e) => return error_to_action_response(e),
    };

    let expanded_command = expand_placeholders(&request.command, &request.args);
    let expanded_command = expand_env_vars(&expanded_command, &request.env);

    if let Err(e) = validate_command_with_specs(&frontmatter.specs, &expanded_command) {
        warn!(
            "Command not allowed by frontmatter: {:?} (file: {})",
            expanded_command, path
        );
        return error_to_action_response(e);
    }

    let tool = match BuiltinTool::from_command(&expanded_command) {
        Ok(t) => t,
        Err(e) => {
            warn!("Unknown tool: {}", e);
            return error_to_action_response(e);
        }
    };

    let working_dir = file_path.parent().unwrap_or(&file_path);
    let executor = ToolExecutor::new(working_dir.to_path_buf(), state.limits.clone());

    info!("Executing tool: {:?}", tool);

    match executor.execute(&tool).await {
        Ok(output) => {
            let response = ActionResponse::success(output.to_text());
            (StatusCode::OK, Json(response)).into_response()
        }
        Err(e) => {
            let status = e.status_code();
            let response = ActionResponse::error(e.user_message());
            (status, Json(response)).into_response()
        }
    }
}

fn error_response(status: StatusCode, message: &str) -> Response {
    let response = ActionResponse::error(message.to_string());
    (status, Json(response)).into_response()
}
