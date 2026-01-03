//! Statespace CLI - serve a tool site from a local directory

use clap::{Parser, Subcommand};
use statespace_server::{build_router, initialize_templates, ExecutionLimits, ServerConfig};
use std::net::SocketAddr;
use std::path::PathBuf;
use std::time::Duration;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Parser, Debug)]
#[command(name = "statespace")]
#[command(author, version, about = "Statespace - AI tool execution runtime")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Serve a tool site from a local directory
    Serve {
        /// Path to the tool site directory (must contain README.md)
        #[arg(value_name = "DIRECTORY")]
        directory: PathBuf,

        /// Host to bind to
        #[arg(short = 'H', long, default_value = "127.0.0.1")]
        host: String,

        /// Port to bind to
        #[arg(short, long, default_value = "8000")]
        port: u16,

        /// Execution timeout in seconds
        #[arg(long, default_value = "30")]
        timeout: u64,

        /// Maximum output size in bytes
        #[arg(long, default_value = "1048576")]
        max_output: usize,

        /// Skip template initialization (don't create AGENTS.md, favicon.svg, index.html)
        #[arg(long)]
        no_init: bool,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "statespace=info,tower_http=info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let cli = Cli::parse();

    match cli.command {
        Commands::Serve {
            directory,
            host,
            port,
            timeout,
            max_output,
            no_init,
        } => {
            run_serve(directory, host, port, timeout, max_output, no_init).await?;
        }
    }

    Ok(())
}

async fn run_serve(
    directory: PathBuf,
    host: String,
    port: u16,
    timeout: u64,
    max_output: usize,
    no_init: bool,
) -> anyhow::Result<()> {
    let directory = directory.canonicalize()?;

    if !directory.is_dir() {
        anyhow::bail!("Path is not a directory: {}", directory.display());
    }

    let readme = directory.join("README.md");
    if !readme.is_file() {
        anyhow::bail!(
            "README.md not found in directory: {}\n\
             A tool site must have a README.md file at its root.",
            directory.display()
        );
    }

    let limits = ExecutionLimits {
        max_output_bytes: max_output,
        timeout: Duration::from_secs(timeout),
        ..Default::default()
    };

    let config = ServerConfig::new(directory.clone())
        .with_host(&host)
        .with_port(port)
        .with_limits(limits);

    if !no_init {
        initialize_templates(&config.content_root, &config.base_url()).await?;
    }

    let router = build_router(config.clone());
    let addr: SocketAddr = config.socket_addr().parse()?;

    tracing::info!("Starting Statespace server");
    tracing::info!("  Content root: {}", directory.display());
    tracing::info!("  Listening on: http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, router).await?;

    Ok(())
}
