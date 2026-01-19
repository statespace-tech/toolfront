//! Command handlers for the CLI

mod app;
mod auth;
mod org;
mod tokens;

use crate::args::{AppCommands, Cli, Commands};
use crate::config;
use crate::error::Result;
use crate::gateway::GatewayClient;

/// Run the CLI with the parsed arguments
pub(crate) async fn run(cli: Cli) -> Result<()> {
    match &cli.command {
        Commands::App { command } => {
            if let AppCommands::Serve(args) = command {
                return app::run_serve(args.clone()).await;
            }
            let gateway = create_gateway(&cli)?;
            app::run(command.clone(), gateway).await
        }
        Commands::Tokens { command } => {
            let gateway = create_gateway(&cli)?;
            tokens::run(command.clone(), gateway).await
        }
        Commands::Auth { command } => {
            // Auth commands don't require existing credentials
            auth::run(command.clone(), cli.global.api_url.as_deref()).await
        }
        Commands::Org { command } => {
            let gateway = create_gateway(&cli)?;
            org::run(command.clone(), gateway).await
        }
    }
}

fn create_gateway(cli: &Cli) -> Result<GatewayClient> {
    let credentials = config::resolve_credentials(
        cli.global.api_url.as_deref(),
        cli.global.api_key.as_deref(),
        cli.global.org_id.as_deref(),
    )?;
    GatewayClient::new(credentials)
}
