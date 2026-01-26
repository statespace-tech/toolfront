//! SSH key management commands.

use std::path::PathBuf;

use crate::args::{SshKeyAddArgs, SshKeyRemoveArgs, SshKeysCommands};
use crate::error::Result;
use crate::gateway::GatewayClient;

/// Run SSH key management commands.
pub(crate) async fn run(command: SshKeysCommands, gateway: GatewayClient) -> Result<()> {
    match command {
        SshKeysCommands::Add(args) => run_add(args, gateway).await,
        SshKeysCommands::List => run_list(gateway).await,
        SshKeysCommands::Remove(args) => run_remove(args, gateway).await,
    }
}

/// Find SSH public keys in ~/.ssh directory.
fn find_ssh_keys() -> Vec<PathBuf> {
    let ssh_dir = dirs::home_dir()
        .map(|h| h.join(".ssh"))
        .filter(|p| p.exists());

    let Some(ssh_dir) = ssh_dir else {
        return Vec::new();
    };

    // Common public key filenames in preference order
    let candidates = ["id_ed25519.pub", "id_rsa.pub", "id_ecdsa.pub", "id_dsa.pub"];

    candidates
        .iter()
        .map(|name| ssh_dir.join(name))
        .filter(|p| p.exists())
        .collect()
}

/// Extract key name from public key content or filename.
fn derive_key_name(key_content: &str, path: &PathBuf) -> String {
    // SSH keys often have a comment at the end: "ssh-ed25519 AAAA... user@host"
    let parts: Vec<&str> = key_content.split_whitespace().collect();
    if parts.len() >= 3 {
        return parts[2..].join(" ");
    }

    // Fall back to filename without extension
    path.file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("ssh-key")
        .to_string()
}

async fn run_add(args: SshKeyAddArgs, gateway: GatewayClient) -> Result<()> {
    let key_path = match args.key_file {
        Some(path) => path,
        None => {
            // Auto-detect SSH keys
            let keys = find_ssh_keys();
            if keys.is_empty() {
                eprintln!("No SSH keys found in ~/.ssh");
                eprintln!("Generate one with: ssh-keygen -t ed25519");
                std::process::exit(1);
            }
            if keys.len() == 1 {
                keys.into_iter().next().unwrap()
            } else {
                // Multiple keys found - prompt user
                eprintln!("Multiple SSH keys found:");
                for (i, key) in keys.iter().enumerate() {
                    eprintln!("  [{}] {}", i + 1, key.display());
                }
                eprintln!("\nSpecify which key to add:");
                eprintln!("  statespace ssh-keys add {}", keys[0].display());
                std::process::exit(1);
            }
        }
    };

    // Read the public key
    let content = std::fs::read_to_string(&key_path).map_err(|e| {
        std::io::Error::new(
            e.kind(),
            format!("Failed to read {}: {}", key_path.display(), e),
        )
    })?;

    let content = content.trim();

    // Validate it looks like an SSH public key
    if !content.starts_with("ssh-") && !content.starts_with("ecdsa-") {
        eprintln!("File doesn't appear to be an SSH public key: {}", key_path.display());
        eprintln!("Expected format: ssh-ed25519 AAAA... comment");
        std::process::exit(1);
    }

    let name = args
        .name
        .unwrap_or_else(|| derive_key_name(content, &key_path));

    eprintln!("Adding SSH key: {}", key_path.display());

    match gateway.add_ssh_key(&name, content).await {
        Ok(key) => {
            eprintln!("SSH key added successfully");
            eprintln!();
            eprintln!("  Name:        {}", key.name);
            eprintln!("  Fingerprint: {}", key.fingerprint);
            eprintln!();
            eprintln!("The key will be available in new and reprovisioned environments.");
            eprintln!("Use `statespace app ssh <app>` to connect.");
            Ok(())
        }
        Err(e) => {
            let msg = e.to_string();
            if msg.contains("402") || msg.contains("Payment Required") {
                eprintln!("SSH access requires a paid plan.");
                eprintln!("Upgrade at https://statespace.dev/settings/billing");
                std::process::exit(1);
            }
            Err(e)
        }
    }
}

async fn run_list(gateway: GatewayClient) -> Result<()> {
    let keys = gateway.list_ssh_keys().await?;

    if keys.is_empty() {
        eprintln!("No SSH keys configured for this organization.");
        eprintln!();
        eprintln!("Add one with: statespace ssh-keys add");
        return Ok(());
    }

    println!("{:<30} {}", "NAME", "FINGERPRINT");
    println!("{}", "-".repeat(70));
    for key in keys {
        println!("{:<30} {}", key.name, key.fingerprint);
    }

    Ok(())
}

async fn run_remove(args: SshKeyRemoveArgs, gateway: GatewayClient) -> Result<()> {
    // Find matching key
    let keys = gateway.list_ssh_keys().await?;
    let matches: Vec<_> = keys
        .iter()
        .filter(|k| k.fingerprint.contains(&args.fingerprint))
        .collect();

    if matches.is_empty() {
        eprintln!("No SSH key found matching: {}", args.fingerprint);
        if !keys.is_empty() {
            eprintln!("\nAvailable keys:");
            for key in &keys {
                eprintln!("  {} ({})", key.fingerprint, key.name);
            }
        }
        std::process::exit(1);
    }

    if matches.len() > 1 {
        eprintln!("Multiple keys match '{}'. Be more specific:", args.fingerprint);
        for key in matches {
            eprintln!("  {} ({})", key.fingerprint, key.name);
        }
        std::process::exit(1);
    }

    let key = matches[0];

    // Confirm deletion
    if !args.yes {
        eprintln!("Remove SSH key?");
        eprintln!("  Name:        {}", key.name);
        eprintln!("  Fingerprint: {}", key.fingerprint);
        eprintln!();
        eprint!("Type 'yes' to confirm: ");

        let mut input = String::new();
        std::io::stdin().read_line(&mut input)?;
        if input.trim() != "yes" {
            eprintln!("Aborted");
            std::process::exit(1);
        }
    }

    gateway.remove_ssh_key(&key.fingerprint).await?;
    eprintln!("SSH key removed: {}", key.name);

    Ok(())
}
