use crate::args::AppSshArgs;
use crate::error::{Error, Result};
use crate::gateway::GatewayClient;
use crate::identifiers::normalize_environment_reference;
use std::process::Stdio;
use tokio::process::Command;

fn ssh_host_from_api_url(api_url: &str) -> String {
    let url = api_url
        .trim_end_matches('/')
        .replace("https://", "")
        .replace("http://", "");

    if url.starts_with("api.staging.") {
        url.replace("api.staging.", "ssh.staging.")
    } else if url.starts_with("api.") {
        url.replace("api.", "ssh.")
    } else {
        format!("ssh.{url}")
    }
}

pub(crate) async fn run_ssh(args: AppSshArgs, gateway: GatewayClient) -> Result<()> {
    let reference = normalize_environment_reference(&args.app).map_err(Error::cli)?;
    let env = gateway.get_environment(reference.value()).await?;

    let short_id: String = env.id.chars().take(8).collect();
    let ssh_host = ssh_host_from_api_url(gateway.base_url());

    eprintln!("Connecting to env-{short_id}@{ssh_host}");

    let status = Command::new("ssh")
        .args(["-o", "StrictHostKeyChecking=no"])
        .args(["-o", "UserKnownHostsFile=/dev/null"])
        .arg(format!("env-{short_id}@{ssh_host}"))
        .stdin(Stdio::inherit())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .status()
        .await
        .map_err(|e| Error::cli(format!("Failed to spawn SSH: {e}")))?;

    if !status.success() {
        if let Some(code) = status.code() {
            std::process::exit(code);
        }
    }

    Ok(())
}
