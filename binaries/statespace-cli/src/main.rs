//! Statespace CLI entry point.

mod args;
mod commands;
mod config;
mod error;
mod gateway;
mod state;

use args::{AppCommands, Cli, Commands};
use clap::Parser;
use config::resolve_credentials;
use error::Result;
use gateway::GatewayClient;

#[tokio::main]
async fn main() {
    if let Err(e) = run().await {
        eprintln!("error: {e}");
        std::process::exit(1);
    }
}

async fn run() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Auth { command } => commands::auth::run(command, cli.api_url.as_deref()).await,

        Commands::Org { command } => {
            let creds = resolve_credentials(
                cli.api_url.as_deref(),
                cli.api_key.as_deref(),
                cli.org_id.as_deref(),
            )?;
            let gateway = GatewayClient::new(creds)?;
            commands::org::run(command, gateway).await
        }

        Commands::App { command } => match command {
            AppCommands::Ssh(args) => {
                let creds = resolve_credentials(
                    cli.api_url.as_deref(),
                    cli.api_key.as_deref(),
                    cli.org_id.as_deref(),
                )?;
                let gateway = GatewayClient::new(creds)?;
                commands::ssh::run_ssh(args, gateway).await
            }
            AppCommands::SshProxy(args) => commands::ssh::run_ssh_proxy(args).await,
        },

        Commands::SshKey { command } => {
            let creds = resolve_credentials(
                cli.api_url.as_deref(),
                cli.api_key.as_deref(),
                cli.org_id.as_deref(),
            )?;
            let gateway = GatewayClient::new(creds)?;
            commands::ssh_key::run(command, gateway).await
        }

        Commands::Ssh { command } => commands::ssh_config::run(command).await,
    }
}
