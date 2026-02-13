use crate::args::ServeArgs;
use crate::error::{Error, Result};
use statespace_server::{ServerConfig, build_router, initialize_templates};
use tokio::net::TcpListener;

pub(crate) async fn run_serve(args: ServeArgs) -> Result<()> {
    let dir = args
        .path
        .canonicalize()
        .map_err(|e| Error::cli(format!("Invalid path '{}': {e}", args.path.display())))?;

    if !dir.is_dir() {
        return Err(Error::cli(format!("Not a directory: {}", dir.display())));
    }

    let config = ServerConfig::new(dir)
        .with_host(args.host)
        .with_port(args.port);

    initialize_templates(&config.content_root, &config.base_url()).await?;

    let addr = config.socket_addr();
    let base_url = config.base_url();
    let router =
        build_router(&config).map_err(|e| Error::cli(format!("Failed to build router: {e}")))?;

    let listener = TcpListener::bind(&addr).await?;
    eprintln!("Serving on {base_url}");

    axum::serve(listener, router)
        .await
        .map_err(|e| Error::cli(format!("Server error: {e}")))?;
    Ok(())
}
