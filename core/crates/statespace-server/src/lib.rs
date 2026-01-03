//! Statespace Server - Open Source AI Tool Execution Runtime
//!
//! This library provides the core functionality for serving AI tool execution
//! environments from markdown files with frontmatter-defined tool specifications.
//!
//! # Features
//!
//! - **Markdown file serving**: Serve markdown files from a local directory
//! - **Frontmatter parsing**: Parse YAML and TOML frontmatter for tool definitions
//! - **Command validation**: Validate commands against tool specifications
//! - **Tool execution**: Execute whitelisted tools in a sandboxed environment
//! - **Security**: Path traversal prevention, environment isolation, SSRF protection
//! - **Landing page**: Auto-generated index.html with agent instructions
//!
//! # Usage
//!
//! ```rust,ignore
//! use statespace_server::{ServerConfig, build_router, initialize_templates};
//! use std::path::PathBuf;
//!
//! let config = ServerConfig::new(PathBuf::from("./my-toolsite"));
//!
//! // Initialize template files (AGENTS.md, favicon.svg, index.html)
//! initialize_templates(&config.content_root, &config.base_url()).await?;
//!
//! let router = build_router(config);
//! ```
//!
//! # Architecture
//!
//! This library follows FP-Rust patterns inspired by Oxide's Omicron:
//!
//! - **Pure modules** (no I/O): `frontmatter`, `validation`, `spec`, `security`, `protocol`, `templates`
//! - **Effectful edge**: `executor`, `content`, `server`, `init`

pub mod content;
pub mod error;
pub mod executor;
pub mod frontmatter;
pub mod init;
pub mod protocol;
pub mod security;
pub mod server;
pub mod spec;
pub mod templates;
pub mod tools;
pub mod validation;

pub use content::{ContentResolver, LocalContentResolver};
pub use error::{Error, Result};
pub use executor::{ExecutionLimits, ToolExecutor};
pub use frontmatter::{parse_frontmatter, Frontmatter};
pub use init::initialize_templates;
pub use protocol::{ActionRequest, ActionResponse};
pub use server::{build_router, ServerConfig, ServerState};
pub use spec::{is_valid_tool_call, ToolPart, ToolSpec};
pub use templates::{render_index_html, AGENTS_MD, FAVICON_SVG};
pub use tools::{BuiltinTool, HttpMethod};
pub use validation::{expand_placeholders, validate_command_with_specs};
