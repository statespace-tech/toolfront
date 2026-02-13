use crate::config::{Credentials, load_stored_credentials};
use crate::error::{Error, Result};
use crate::gateway::GatewayClient;
use inquire::Confirm;
use std::fs;
use std::path::Path;
use std::process::Command;

const STATESPACE_CONFIG_FILENAME: &str = "statespace_config";
const INCLUDE_LINE: &str = "Include ~/.ssh/statespace_config";

const STATESPACE_SSH_CONFIG: &str = r"# --- BEGIN STATESPACE MANAGED ---
Host *.statespace
  User env
  RequestTTY auto
  ServerAliveInterval 30
  ServerAliveCountMax 3
  TCPKeepAlive yes
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
# --- END STATESPACE MANAGED ---
";

pub(crate) async fn run_setup(yes: bool) -> Result<()> {
    let Some(stored) = load_stored_credentials()? else {
        eprintln!("Not logged in. Run 'statespace auth login' first.");
        std::process::exit(1);
    };

    let credentials = Credentials {
        api_url: stored.api_url,
        api_key: stored.api_key,
        org_id: Some(stored.org_id),
    };

    let gateway = GatewayClient::new(credentials)?;
    setup_ssh_full(&gateway, yes).await
}

pub(crate) fn run_uninstall(yes: bool) -> Result<()> {
    uninstall(yes)
}

fn ssh_dir() -> Result<std::path::PathBuf> {
    dirs::home_dir()
        .map(|h| h.join(".ssh"))
        .ok_or_else(|| Error::cli("Could not determine home directory"))
}

fn find_ssh_key() -> Option<std::path::PathBuf> {
    let ssh_dir = ssh_dir().ok()?;
    for name in ["id_ed25519.pub", "id_ecdsa.pub", "id_rsa.pub"] {
        let path = ssh_dir.join(name);
        if path.exists() {
            return Some(path);
        }
    }
    None
}

fn generate_ssh_key() -> Result<std::path::PathBuf> {
    let ssh_dir = ssh_dir()?;
    let key_path = ssh_dir.join("id_ed25519");

    if !ssh_dir.exists() {
        fs::create_dir_all(&ssh_dir)
            .map_err(|e| Error::cli(format!("Failed to create ~/.ssh: {e}")))?;
        set_dir_permissions(&ssh_dir);
    }

    let status = Command::new("ssh-keygen")
        .args(["-t", "ed25519", "-f"])
        .arg(&key_path)
        .args(["-N", ""])
        .status()
        .map_err(|e| Error::cli(format!("Failed to run ssh-keygen: {e}")))?;

    if !status.success() {
        return Err(Error::cli("ssh-keygen failed"));
    }

    Ok(key_path.with_extension("pub"))
}

fn compute_ssh_fingerprint(key_path: &Path) -> Result<String> {
    let output = Command::new("ssh-keygen")
        .args(["-lf"])
        .arg(key_path)
        .output()
        .map_err(|e| Error::cli(format!("Failed to run ssh-keygen: {e}")))?;

    if !output.status.success() {
        return Err(Error::cli("Failed to compute key fingerprint"));
    }

    String::from_utf8_lossy(&output.stdout)
        .split_whitespace()
        .nth(1)
        .map(String::from)
        .ok_or_else(|| Error::cli("Failed to parse fingerprint"))
}

async fn upload_ssh_key(gateway: &GatewayClient, key_path: &Path) -> Result<bool> {
    let key_content = fs::read_to_string(key_path)
        .map_err(|e| Error::cli(format!("Failed to read '{}': {e}", key_path.display())))?;
    let key_content = key_content.trim();
    let fingerprint = compute_ssh_fingerprint(key_path)?;

    let existing = gateway.list_ssh_keys().await?;
    if existing.iter().any(|k| k.fingerprint == fingerprint) {
        return Ok(false);
    }

    let name = derive_key_name(key_content);
    gateway.add_ssh_key(&name, key_content).await?;
    Ok(true)
}

fn derive_key_name(key_content: &str) -> String {
    let parts: Vec<&str> = key_content.split_whitespace().collect();
    if parts.len() >= 3 {
        parts[2..].join(" ")
    } else {
        let hostname = Command::new("hostname")
            .output()
            .ok()
            .and_then(|o| String::from_utf8(o.stdout).ok())
            .map_or_else(|| "unknown".to_string(), |s| s.trim().to_string());
        format!("statespace-cli-{hostname}")
    }
}

pub(crate) async fn setup_ssh_full(gateway: &GatewayClient, skip_prompt: bool) -> Result<()> {
    let key_path = if let Some(path) = find_ssh_key() {
        path
    } else {
        if !skip_prompt {
            let generate = Confirm::new("No SSH key found. Generate a new ed25519 key?")
                .with_default(true)
                .prompt()
                .map_err(|e| Error::cli(format!("Prompt failed: {e}")))?;

            if !generate {
                println!("Skipped SSH key generation.");
                return Ok(());
            }
        }

        println!("Generating SSH key...");
        let path = generate_ssh_key()?;
        println!("✓ Generated {}", path.display());
        path
    };

    match upload_ssh_key(gateway, &key_path).await {
        Ok(true) => {
            let fp = compute_ssh_fingerprint(&key_path).unwrap_or_default();
            println!("✓ Uploaded SSH key ({fp})");
        }
        Ok(false) => println!("✓ SSH key already registered"),
        Err(e) => {
            if is_payment_required(&e) {
                eprintln!("Note: SSH access requires a paid plan.");
                eprintln!("Upgrade at https://statespace.dev/settings/billing");
            } else {
                eprintln!("Note: Failed to upload SSH key: {e}");
            }
        }
    }

    configure_ssh_config()?;

    println!();
    println!("You can now use:");
    println!("  ssh env@<environment>.statespace");
    println!("  scp file.txt env@<environment>.statespace:~");
    println!("  rsync -av ./dir env@<environment>.statespace:~");

    Ok(())
}

fn configure_ssh_config() -> Result<()> {
    let statespace_path = statespace_config_path()?;
    let config_path = ssh_config_path()?;
    let ssh_dir = ssh_dir()?;

    if statespace_path.exists() && config_has_include(&config_path)? {
        println!("✓ SSH configuration already set up");
        return Ok(());
    }

    if !ssh_dir.exists() {
        fs::create_dir_all(&ssh_dir)
            .map_err(|e| Error::cli(format!("Failed to create ~/.ssh: {e}")))?;
        set_dir_permissions(&ssh_dir);
    }

    fs::write(&statespace_path, STATESPACE_SSH_CONFIG).map_err(|e| {
        Error::cli(format!(
            "Failed to write {}: {e}",
            statespace_path.display()
        ))
    })?;
    set_file_permissions(&statespace_path);

    if !config_has_include(&config_path)? {
        add_include_to_config(&config_path)?;
    }

    println!("✓ Configured ~/.ssh/config");
    Ok(())
}

#[cfg(unix)]
fn set_dir_permissions(path: &Path) {
    use std::os::unix::fs::PermissionsExt;
    let _ = fs::set_permissions(path, fs::Permissions::from_mode(0o700));
}

#[cfg(not(unix))]
fn set_dir_permissions(_path: &Path) {}

#[cfg(unix)]
fn set_file_permissions(path: &Path) {
    use std::os::unix::fs::PermissionsExt;
    let _ = fs::set_permissions(path, fs::Permissions::from_mode(0o600));
}

#[cfg(not(unix))]
fn set_file_permissions(_path: &Path) {}

fn statespace_config_path() -> Result<std::path::PathBuf> {
    Ok(ssh_dir()?.join(STATESPACE_CONFIG_FILENAME))
}

fn ssh_config_path() -> Result<std::path::PathBuf> {
    Ok(ssh_dir()?.join("config"))
}

fn config_has_include(path: &Path) -> Result<bool> {
    if !path.exists() {
        return Ok(false);
    }

    let content = fs::read_to_string(path)
        .map_err(|e| Error::cli(format!("Failed to read {}: {e}", path.display())))?;

    Ok(content.lines().any(|line| {
        let trimmed = line.trim();
        trimmed == INCLUDE_LINE || trimmed == "Include ~/.ssh/statespace_config"
    }))
}

fn add_include_to_config(path: &Path) -> Result<()> {
    let existing = if path.exists() {
        fs::read_to_string(path)
            .map_err(|e| Error::cli(format!("Failed to read {}: {e}", path.display())))?
    } else {
        String::new()
    };

    let new_content = if existing.is_empty() {
        format!("{INCLUDE_LINE}\n")
    } else {
        format!("{INCLUDE_LINE}\n\n{existing}")
    };

    fs::write(path, &new_content)
        .map_err(|e| Error::cli(format!("Failed to write {}: {e}", path.display())))?;
    set_file_permissions(path);

    Ok(())
}

fn is_payment_required(err: &crate::error::Error) -> bool {
    matches!(
        err,
        crate::error::Error::Gateway(crate::error::GatewayError::Api { status: 402, .. })
    )
}

fn uninstall(skip_prompt: bool) -> Result<()> {
    let statespace_path = statespace_config_path()?;
    let config_path = ssh_config_path()?;

    let statespace_exists = statespace_path.exists();
    let has_include = config_has_include(&config_path)?;

    if !statespace_exists && !has_include {
        println!("✓ No Statespace SSH configuration found.");
        return Ok(());
    }

    println!("This will remove Statespace SSH configuration.");
    println!();
    if statespace_exists {
        println!("  • Delete {}", statespace_path.display());
    }
    if has_include {
        println!("  • Remove include from {}", config_path.display());
    }
    println!();

    if !skip_prompt {
        let confirmed = Confirm::new("Proceed with uninstall?")
            .with_default(false)
            .prompt()
            .map_err(|e| Error::cli(format!("Prompt failed: {e}")))?;

        if !confirmed {
            println!("Aborted.");
            return Ok(());
        }
    }

    if statespace_exists {
        fs::remove_file(&statespace_path).map_err(|e| {
            Error::cli(format!(
                "Failed to delete {}: {e}",
                statespace_path.display()
            ))
        })?;
        println!("✓ Deleted {}", statespace_path.display());
    }

    if has_include {
        remove_include_from_config(&config_path)?;
        println!("✓ Updated {}", config_path.display());
    }

    println!();
    println!("SSH configuration removed.");
    Ok(())
}

fn remove_include_from_config(path: &Path) -> Result<()> {
    let content = fs::read_to_string(path)
        .map_err(|e| Error::cli(format!("Failed to read {}: {e}", path.display())))?;

    let new_content: String = content
        .lines()
        .filter(|line| {
            let trimmed = line.trim();
            trimmed != INCLUDE_LINE && trimmed != "Include ~/.ssh/statespace_config"
        })
        .collect::<Vec<_>>()
        .join("\n");

    let new_content = new_content.trim_start_matches('\n').to_string() + "\n";

    fs::write(path, new_content.trim_start())
        .map_err(|e| Error::cli(format!("Failed to write {}: {e}", path.display())))
}
