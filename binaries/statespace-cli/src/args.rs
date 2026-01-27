//! CLI argument definitions using clap derive.

use clap::{Parser, Subcommand, ValueEnum};

#[derive(Debug, Parser)]
#[command(name = "statespace")]
#[command(about = "Statespace CLI - deploy and manage environments")]
#[command(version)]
pub(crate) struct Cli {
    /// API URL override
    #[arg(long, global = true, env = "STATESPACE_API_URL")]
    pub api_url: Option<String>,

    /// API key override
    #[arg(long, global = true, env = "STATESPACE_API_KEY")]
    pub api_key: Option<String>,

    /// Organization ID override
    #[arg(long, global = true, env = "STATESPACE_ORG_ID")]
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

    /// SSH key management
    #[command(name = "ssh-key")]
    SshKey {
        #[command(subcommand)]
        command: SshKeyCommands,
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
    /// SSH into an environment
    Ssh(AppSshArgs),

    /// Internal: SSH proxy command (used by ProxyCommand)
    #[command(name = "ssh-proxy", hide = true)]
    SshProxy(AppSshProxyArgs),
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
pub(crate) struct AppSshProxyArgs {
    /// Environment ID or name
    pub app: String,

    /// Target host within the environment
    #[arg(long, default_value = "localhost")]
    pub host: String,

    /// Target port within the environment
    #[arg(long, short, default_value = "22")]
    pub port: u16,
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
        /// Key ID to remove
        id: String,
    },
}
