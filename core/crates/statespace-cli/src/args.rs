//! CLI argument definitions using clap

use clap::{Args, Parser, Subcommand};
use std::path::PathBuf;

#[derive(Debug, Parser)]
#[command(name = "statespace")]
#[command(author, version, about = "Statespace - AI tool execution runtime")]
pub(crate) struct Cli {
    #[command(flatten)]
    pub global: GlobalArgs,

    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Debug, Args)]
pub(crate) struct GlobalArgs {
    /// API gateway URL (default: https://api.statespace.com)
    #[arg(long, global = true)]
    pub api_url: Option<String>,

    /// API key for authentication
    #[arg(long, global = true, env = "STATESPACE_API_KEY")]
    pub api_key: Option<String>,

    /// Organization ID (required for token operations)
    #[arg(long, global = true)]
    pub org_id: Option<String>,
}

#[derive(Debug, Subcommand)]
pub(crate) enum Commands {
    /// Manage and serve tool site applications
    App {
        #[command(subcommand)]
        command: AppCommands,
    },

    /// Manage personal access tokens
    Tokens {
        #[command(subcommand)]
        command: TokensCommands,
    },
}

#[derive(Debug, Clone, Subcommand)]
pub(crate) enum AppCommands {
    /// Serve a tool site from a local directory
    Serve(AppServeArgs),

    /// Deploy a tool site to the cloud
    Deploy(AppDeployArgs),

    /// List deployed apps
    List,

    /// Update an existing app with new content
    Update(AppUpdateArgs),

    /// Delete a deployed app
    Delete(AppDeleteArgs),
}

#[derive(Debug, Clone, Args)]
pub(crate) struct AppServeArgs {
    /// Path to the tool site directory (must contain README.md)
    #[arg(value_name = "DIRECTORY", default_value = ".")]
    pub directory: PathBuf,

    /// Host to bind to
    #[arg(short = 'H', long, default_value = "127.0.0.1")]
    pub host: String,

    /// Port to bind to
    #[arg(short, long, default_value_t = 8000)]
    pub port: u16,

    /// Execution timeout in seconds
    #[arg(long, default_value_t = 30)]
    pub timeout: u64,

    /// Maximum output size in bytes
    #[arg(long, default_value_t = 1_048_576)]
    pub max_output: usize,

    /// Skip template initialization
    #[arg(long)]
    pub no_init: bool,
}

#[derive(Debug, Clone, Args)]
pub(crate) struct AppDeployArgs {
    /// Path to the tool site directory
    #[arg(value_name = "PATH", default_value = ".")]
    pub path: PathBuf,

    /// App name (defaults to directory name)
    #[arg(long)]
    pub name: Option<String>,

    /// Wait for the app to be ready
    #[arg(long)]
    pub verify: bool,
}

#[derive(Debug, Clone, Args)]
pub(crate) struct AppUpdateArgs {
    /// App ID to update
    #[arg(value_name = "ID")]
    pub id: String,

    /// Path to the tool site directory
    #[arg(value_name = "PATH", default_value = ".")]
    pub path: PathBuf,
}

#[derive(Debug, Clone, Args)]
pub(crate) struct AppDeleteArgs {
    /// App ID to delete
    #[arg(value_name = "ID")]
    pub id: String,

    /// Skip confirmation prompt
    #[arg(long, short)]
    pub yes: bool,
}

#[derive(Debug, Clone, Subcommand)]
pub(crate) enum TokensCommands {
    /// Create a new personal access token
    Create(TokenCreateArgs),

    /// List all tokens
    List(TokenListArgs),

    /// Get details for a specific token
    Get(TokenGetArgs),

    /// Rotate a token (generates new value, revokes old)
    Rotate(TokenRotateArgs),

    /// Revoke a token (cannot be undone)
    Revoke(TokenRevokeArgs),
}

#[derive(Debug, Clone, Args)]
pub(crate) struct TokenCreateArgs {
    /// Name for the token
    #[arg(long)]
    pub name: String,

    /// Token scope (read, execute, admin)
    #[arg(long, default_value = "execute")]
    pub scope: String,

    /// Restrict to specific app IDs
    #[arg(long = "app")]
    pub app_ids: Vec<String>,

    /// Expiration date (ISO 8601 format)
    #[arg(long)]
    pub expires: Option<String>,
}

#[derive(Debug, Clone, Args)]
pub(crate) struct TokenListArgs {
    /// Show inactive tokens too
    #[arg(long)]
    pub all: bool,

    /// Maximum number of tokens to return
    #[arg(long, default_value_t = 100)]
    pub limit: u32,
}

#[derive(Debug, Clone, Args)]
pub(crate) struct TokenGetArgs {
    /// Token ID
    pub token_id: String,
}

#[derive(Debug, Clone, Args)]
pub(crate) struct TokenRotateArgs {
    /// Token ID to rotate
    pub token_id: String,

    /// New name for the token
    #[arg(long)]
    pub name: Option<String>,

    /// New scope (read, execute, admin)
    #[arg(long)]
    pub scope: Option<String>,

    /// New app restrictions
    #[arg(long = "app")]
    pub app_ids: Vec<String>,

    /// New expiration date
    #[arg(long)]
    pub expires: Option<String>,
}

#[derive(Debug, Clone, Args)]
pub(crate) struct TokenRevokeArgs {
    /// Token ID to revoke
    pub token_id: String,

    /// Reason for revocation
    #[arg(long)]
    pub reason: Option<String>,

    /// Skip confirmation prompt
    #[arg(long, short)]
    pub yes: bool,
}
