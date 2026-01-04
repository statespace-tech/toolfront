//! Statespace CLI - AI tool execution runtime

mod args;
mod commands;
mod config;
mod error;
mod gateway;

use clap::Parser;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "statespace=info,tower_http=info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let cli = args::Cli::parse();

    if let Err(e) = commands::run(cli).await {
        eprintln!("error: {e}");
        std::process::exit(1);
    }
}
