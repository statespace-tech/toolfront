use clap::{Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

#[derive(Debug, Parser)]
#[command(name = "statespace")]
#[command(about = "Statespace CLI - deploy and manage environments")]
#[command(version)]
pub(crate) struct Cli {
    /// API key override
    #[arg(long, global = true)]
    pub api_key: Option<String>,

    /// Organization ID override
    #[arg(long, global = true)]
    pub org_id: Option<String>,

    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Debug, Subcommand)]
pub(crate) enum Commands {
    /// Authentication commands
    Auth {
        #[command(subcommand)]
        command: AuthCommands,
    },

    /// Organization commands
    Org {
        #[command(subcommand)]
        command: OrgCommands,
    },

    /// Application commands
    App {
        #[command(subcommand)]
        command: AppCommands,
    },

    /// Serve a local app (no account required)
    Serve(ServeArgs),

    /// SSH configuration management
    Ssh {
        #[command(subcommand)]
        command: SshCommands,
    },

    /// Token management commands
    Tokens {
        #[command(subcommand)]
        command: TokensCommands,
    },
}

#[derive(Debug, Subcommand)]
pub(crate) enum AuthCommands {
    /// Log in via browser (device auth flow)
    Login,

    /// Log out and clear stored credentials
    Logout,

    /// Show current authentication status
    Status,

    /// Print the current API token
    Token {
        /// Output format
        #[arg(long, short, default_value = "plain")]
        format: TokenOutputFormat,
    },
}

#[derive(Debug, Clone, Copy, Default, ValueEnum)]
pub(crate) enum TokenOutputFormat {
    #[default]
    Plain,
    Json,
}

#[derive(Debug, Subcommand)]
pub(crate) enum OrgCommands {
    /// List available organizations
    List,

    /// Show current organization
    Current,

    /// Switch to a different organization
    Use {
        /// Organization name or ID (interactive if omitted)
        org: Option<String>,
    },
}

#[derive(Debug, Subcommand)]
pub(crate) enum AppCommands {
    /// Create a new environment
    Create(AppCreateArgs),

    /// Create a new environment (alias for create)
    #[command(hide = true)]
    Deploy(AppCreateArgs),

    /// List all environments
    List,

    /// Show details for an environment
    Get(AppGetArgs),

    /// Delete an environment
    Delete(AppDeleteArgs),

    /// Sync markdown files to an environment (create-or-update)
    Sync(AppSyncArgs),

    /// SSH into an environment
    Ssh(AppSshArgs),
}

#[derive(Debug, Parser)]
pub(crate) struct AppSshArgs {
    /// Environment ID or name
    pub app: String,

    /// SSH user (default: env)
    #[arg(long, short, default_value = "env")]
    pub user: String,

    /// SSH port (default: 22)
    #[arg(long, short, default_value = "22")]
    pub port: u16,
}

#[derive(Debug, Parser)]
pub(crate) struct AppSyncArgs {
    /// Directory to sync (default: current directory)
    #[arg(default_value = ".")]
    pub path: PathBuf,

    /// Environment name (default: directory name)
    #[arg(long, short)]
    pub name: Option<String>,
}

#[derive(Debug, Parser)]
pub(crate) struct ServeArgs {
    /// Directory to serve (default: current directory)
    #[arg(default_value = ".")]
    pub path: PathBuf,

    /// Host to bind the server to
    #[arg(long, default_value = "127.0.0.1")]
    pub host: String,

    /// Port to bind the server to
    #[arg(long, default_value = "8000")]
    pub port: u16,
}

#[derive(Debug, Clone, Copy, Default, ValueEnum)]
pub(crate) enum VisibilityArg {
    #[default]
    Public,
    Private,
}

#[derive(Debug, Parser)]
pub(crate) struct AppCreateArgs {
    /// Directory containing markdown files (optional — omit to create an empty environment)
    pub path: Option<PathBuf>,

    /// Environment name (default: directory name, or required if no path given)
    #[arg(long, short)]
    pub name: Option<String>,

    /// Environment visibility
    #[arg(long, default_value = "public")]
    pub visibility: VisibilityArg,

    /// Wait for the environment to become ready
    #[arg(long)]
    pub verify: bool,
}

#[derive(Debug, Parser)]
pub(crate) struct AppGetArgs {
    /// Environment ID or name
    pub id: String,
}

#[derive(Debug, Parser)]
pub(crate) struct AppDeleteArgs {
    /// Environment ID or name
    pub id: String,

    /// Skip confirmation prompt
    #[arg(long, short)]
    pub yes: bool,
}

#[derive(Debug, Subcommand)]
pub(crate) enum SshKeyCommands {
    /// List your SSH public keys
    List,

    /// Add an SSH public key
    Add {
        /// Path to public key file (default: ~/.ssh/id_ed25519.pub or ~/.ssh/id_rsa.pub)
        #[arg(long, short)]
        file: Option<String>,

        /// Key name/label
        #[arg(long, short)]
        name: Option<String>,
    },

    /// Remove an SSH public key
    Remove {
        /// Key fingerprint to remove
        fingerprint: String,
    },
}

#[derive(Debug, Subcommand)]
pub(crate) enum SshCommands {
    /// Configure SSH for native scp/rsync/ssh access
    Setup {
        /// Skip confirmation prompt
        #[arg(long)]
        yes: bool,
    },
    /// Remove Statespace SSH configuration
    Uninstall {
        /// Skip confirmation prompt
        #[arg(long)]
        yes: bool,
    },
    /// SSH key management
    Keys {
        #[command(subcommand)]
        command: SshKeyCommands,
    },
}

#[derive(Debug, Subcommand)]
pub(crate) enum TokensCommands {
    /// Create a new personal access token
    Create(TokenCreateArgs),

    /// List personal access tokens
    List(TokenListArgs),

    /// Show details for a token
    Get(TokenGetArgs),

    /// Rotate a token (revoke old, issue new)
    Rotate(TokenRotateArgs),

    /// Revoke a token
    Revoke(TokenRevokeArgs),
}

#[derive(Debug, Parser)]
pub(crate) struct TokenCreateArgs {
    /// Token name
    pub name: String,

    /// Token scope (read or admin)
    #[arg(long, short, default_value = "read")]
    pub scope: String,

    /// Restrict token to specific environment IDs
    #[arg(long = "app-id")]
    pub app_ids: Vec<String>,

    /// Expiration (ISO 8601 datetime, e.g. 2026-12-31T00:00:00Z)
    #[arg(long)]
    pub expires: Option<String>,
}

#[derive(Debug, Parser)]
pub(crate) struct TokenListArgs {
    /// Show all tokens including revoked
    #[arg(long, short)]
    pub all: bool,

    /// Maximum number of tokens to return
    #[arg(long, short, default_value = "100")]
    pub limit: u32,
}

#[derive(Debug, Parser)]
pub(crate) struct TokenGetArgs {
    /// Token ID
    pub token_id: String,
}

#[derive(Debug, Parser)]
pub(crate) struct TokenRotateArgs {
    /// Token ID to rotate
    pub token_id: String,

    /// New name
    #[arg(long)]
    pub name: Option<String>,

    /// New scope (read or admin)
    #[arg(long)]
    pub scope: Option<String>,

    /// Restrict to specific environment IDs
    #[arg(long = "app-id")]
    pub app_ids: Vec<String>,

    /// New expiration (ISO 8601 datetime)
    #[arg(long)]
    pub expires: Option<String>,
}

#[derive(Debug, Parser)]
pub(crate) struct TokenRevokeArgs {
    /// Token ID to revoke
    pub token_id: String,

    /// Revocation reason
    #[arg(long, short)]
    pub reason: Option<String>,

    /// Skip confirmation prompt
    #[arg(long, short)]
    pub yes: bool,
}
