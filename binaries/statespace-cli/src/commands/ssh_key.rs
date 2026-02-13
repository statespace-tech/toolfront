use crate::args::SshKeyCommands;
use crate::error::{Error, Result};
use crate::gateway::GatewayClient;
use std::path::PathBuf;

pub(crate) async fn run(cmd: SshKeyCommands, gateway: GatewayClient) -> Result<()> {
    match cmd {
        SshKeyCommands::List => run_list(gateway).await,
        SshKeyCommands::Add { file, name } => run_add(file, name, gateway).await,
        SshKeyCommands::Remove { fingerprint } => run_remove(&fingerprint, gateway).await,
    }
}

async fn run_list(gateway: GatewayClient) -> Result<()> {
    let keys = gateway.list_ssh_keys().await?;

    if keys.is_empty() {
        println!("No SSH keys found.");
        println!();
        println!("Add a key with: statespace ssh keys add");
        return Ok(());
    }

    println!();
    for key in keys {
        println!("  {} ({})", key.name, key.id);
        println!("    Fingerprint: {}", key.fingerprint);
        println!("    Created: {}", key.created_at);
        println!();
    }

    Ok(())
}

async fn run_add(file: Option<String>, name: Option<String>, gateway: GatewayClient) -> Result<()> {
    let key_path = match file {
        Some(f) => PathBuf::from(f),
        None => find_default_key()?,
    };

    let public_key = std::fs::read_to_string(&key_path).map_err(|e| {
        Error::cli(format!(
            "Failed to read public key '{}': {e}",
            key_path.display()
        ))
    })?;

    let public_key = public_key.trim();

    if !public_key.starts_with("ssh-") && !public_key.starts_with("ecdsa-") {
        return Err(Error::cli(format!(
            "Invalid SSH public key format in '{}'",
            key_path.display()
        )));
    }

    let key_name = name.unwrap_or_else(|| {
        key_path
            .file_stem()
            .and_then(|s| s.to_str())
            .map_or_else(|| "cli-key".to_string(), std::string::ToString::to_string)
    });

    let key = gateway.add_ssh_key(&key_name, public_key).await?;

    println!("✓ Added SSH key: {} ({})", key.name, key.id);
    println!("  Fingerprint: {}", key.fingerprint);

    Ok(())
}

async fn run_remove(fingerprint: &str, gateway: GatewayClient) -> Result<()> {
    gateway.remove_ssh_key(fingerprint).await?;
    println!("✓ Removed SSH key: {fingerprint}");
    Ok(())
}

fn find_default_key() -> Result<PathBuf> {
    let home = dirs::home_dir().ok_or_else(|| Error::cli("Cannot determine home directory"))?;
    let ssh_dir = home.join(".ssh");

    let candidates = ["id_ed25519.pub", "id_rsa.pub", "id_ecdsa.pub"];

    for name in candidates {
        let path = ssh_dir.join(name);
        if path.exists() {
            return Ok(path);
        }
    }

    Err(Error::cli(format!(
        "No SSH public key found in {}. Specify one with --file.",
        ssh_dir.display()
    )))
}
