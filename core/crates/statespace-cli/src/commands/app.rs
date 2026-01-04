//! App subcommand handlers

use crate::args::{AppCommands, AppDeleteArgs, AppDeployArgs, AppServeArgs, AppUpdateArgs};
use crate::error::{Error, Result};
use crate::gateway::GatewayClient;
use statespace_server::{build_router, initialize_templates, ExecutionLimits, ServerConfig};
use std::io::{self, Write};
use std::net::SocketAddr;
use std::time::Duration;

pub(crate) async fn run(cmd: AppCommands, gateway: GatewayClient) -> Result<()> {
    match cmd {
        AppCommands::Serve(_) => unreachable!("serve handled separately"),
        AppCommands::Deploy(args) => run_deploy(args, gateway).await,
        AppCommands::List => run_list(gateway).await,
        AppCommands::Update(args) => run_update(args, gateway).await,
        AppCommands::Delete(args) => run_delete(args, gateway).await,
    }
}

pub(crate) async fn run_serve(args: AppServeArgs) -> Result<()> {
    let directory = args.directory.canonicalize().map_err(|e| {
        Error::cli(format!(
            "Cannot access directory '{}': {e}",
            args.directory.display()
        ))
    })?;

    if !directory.is_dir() {
        return Err(Error::cli(format!(
            "Path is not a directory: {}",
            directory.display()
        )));
    }

    let readme = directory.join("README.md");
    if !readme.is_file() {
        return Err(Error::cli(format!(
            "README.md not found in directory: {}\n\
             A tool site must have a README.md file at its root.",
            directory.display()
        )));
    }

    let limits = ExecutionLimits {
        max_output_bytes: args.max_output,
        timeout: Duration::from_secs(args.timeout),
        ..Default::default()
    };

    let config = ServerConfig::new(directory.clone())
        .with_host(&args.host)
        .with_port(args.port)
        .with_limits(limits);

    if !args.no_init {
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

async fn run_deploy(args: AppDeployArgs, gateway: GatewayClient) -> Result<()> {
    let dir_path = if args.path.is_dir() {
        args.path.clone()
    } else {
        args.path
            .parent()
            .map(|p| p.to_path_buf())
            .unwrap_or_else(|| args.path.clone())
    };

    let name = args.name.unwrap_or_else(|| {
        dir_path
            .file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("app")
            .to_string()
    });

    println!("Scanning {}...", dir_path.display());
    let files = gateway.scan_markdown_files(&dir_path)?;

    if files.is_empty() {
        return Err(Error::cli("No markdown files found"));
    }

    println!("Found {} file(s)", files.len());
    println!("\nDeploying '{name}'...");

    let result = gateway.deploy_environment(&name, files).await?;

    println!();
    println!("{}", "─".repeat(80));
    println!("  App ID:  {}", result.id);
    if let Some(url) = &result.url {
        println!("  URL:     {url}");
    }
    if let Some(fly_url) = &result.fly_url {
        println!("  Fly URL: {fly_url}");
    }
    if let Some(token) = &result.auth_token {
        println!("  Token:   {token}");
    }
    println!("{}", "─".repeat(80));
    println!("\n✓ Deployment created");

    if args.verify
        && let (Some(url), Some(token)) = (&result.url, &result.auth_token)
    {
        println!("\nWaiting for app to be ready...");
        if gateway.verify_environment(url, token).await? {
            println!("✓ App is ready!");
        } else {
            println!("Verification timed out. App may still be starting.");
        }
    }

    Ok(())
}

async fn run_list(gateway: GatewayClient) -> Result<()> {
    let envs = gateway.list_environments().await?;

    if envs.is_empty() {
        println!("No apps found");
        return Ok(());
    }

    println!("\n{} app(s)\n", envs.len());
    println!("{:<30} {:<12} {:<38} URL", "NAME", "STATUS", "ID");
    println!("{}", "─".repeat(120));

    for env in envs {
        let status = match env.status.as_str() {
            "running" => format!("✓ {}", env.status),
            "pending" => format!("⏳ {}", env.status),
            _ => format!("✗ {}", env.status),
        };
        let url = env.url.as_deref().unwrap_or("-");
        let id_short = if env.id.len() > 36 {
            &env.id[..36]
        } else {
            &env.id
        };

        println!("{:<30} {:<12} {:<38} {}", env.name, status, id_short, url);
    }

    Ok(())
}

async fn run_update(args: AppUpdateArgs, gateway: GatewayClient) -> Result<()> {
    let dir_path = if args.path.is_dir() {
        args.path.clone()
    } else {
        args.path
            .parent()
            .map(|p| p.to_path_buf())
            .unwrap_or_else(|| args.path.clone())
    };

    println!("Scanning {}...", dir_path.display());
    let files = gateway.scan_markdown_files(&dir_path)?;

    if files.is_empty() {
        return Err(Error::cli("No markdown files found"));
    }

    println!("Found {} file(s)", files.len());
    println!("\nUpdating app {}...", args.id);

    gateway.update_environment(&args.id, files).await?;

    println!();
    println!("{}", "─".repeat(80));
    println!("  ✓ App updated successfully");
    println!("  Files uploaded and search index updated");
    println!("{}", "─".repeat(80));

    Ok(())
}

async fn run_delete(args: AppDeleteArgs, gateway: GatewayClient) -> Result<()> {
    if !args.yes {
        print!("Are you sure you want to delete app {}? [y/N] ", args.id);
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;

        if !input.trim().eq_ignore_ascii_case("y") {
            println!("Cancelled");
            return Ok(());
        }
    }

    gateway.delete_environment(&args.id).await?;
    println!("✓ App {} deleted", args.id);

    Ok(())
}
