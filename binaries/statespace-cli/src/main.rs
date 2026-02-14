mod args;
mod commands;
mod config;
mod error;
mod gateway;
mod identifiers;
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
        Commands::Auth { command } => commands::auth::run(command).await,

        Commands::Serve(args) => commands::serve::run_serve(args).await,

        Commands::Org { command } => {
            let creds = resolve_credentials(cli.api_key.as_deref(), cli.org_id.as_deref())?;
            let gateway = GatewayClient::new(creds)?;
            commands::org::run(command, gateway).await
        }

        Commands::App { command } => {
            let build_gateway = || -> Result<GatewayClient> {
                let creds = resolve_credentials(cli.api_key.as_deref(), cli.org_id.as_deref())?;
                GatewayClient::new(creds)
            };

            match command {
                AppCommands::Create(args) | AppCommands::Deploy(args) => {
                    let gateway = build_gateway()?;
                    commands::app::run_create(args, gateway).await
                }
                AppCommands::List => {
                    let gateway = build_gateway()?;
                    commands::app::run_list(gateway).await
                }
                AppCommands::Get(args) => {
                    let gateway = build_gateway()?;
                    commands::app::run_get(args, gateway).await
                }
                AppCommands::Delete(args) => {
                    let gateway = build_gateway()?;
                    commands::app::run_delete(args, gateway).await
                }
                AppCommands::Sync(args) => {
                    let gateway = build_gateway()?;
                    commands::sync::run_sync(args, gateway).await
                }
                AppCommands::Ssh(args) => {
                    let gateway = build_gateway()?;
                    commands::ssh::run_ssh(args, gateway).await
                }
            }
        }

        Commands::Tokens { command } => {
            let creds = resolve_credentials(cli.api_key.as_deref(), cli.org_id.as_deref())?;
            let gateway = GatewayClient::new(creds)?;
            commands::tokens::run(command, gateway).await
        }

        Commands::Ssh { command } => match command {
            args::SshCommands::Setup { yes } => commands::ssh_config::run_setup(yes).await,
            args::SshCommands::Uninstall { yes } => commands::ssh_config::run_uninstall(yes),
            args::SshCommands::Keys { command } => {
                let creds = resolve_credentials(cli.api_key.as_deref(), cli.org_id.as_deref())?;
                let gateway = GatewayClient::new(creds)?;
                commands::ssh_key::run(command, gateway).await
            }
        },
    }
}
