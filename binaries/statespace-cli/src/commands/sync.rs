use crate::args::AppSyncArgs;
use crate::error::Result;
use crate::gateway::GatewayClient;
use crate::state::{SyncState, load_state, save_state};

pub(crate) async fn run_sync(args: AppSyncArgs, gateway: GatewayClient) -> Result<()> {
    let dir = args.path.canonicalize().map_err(|e| {
        crate::error::Error::cli(format!("Invalid path '{}': {e}", args.path.display()))
    })?;

    let cached = load_state(&dir)?;

    let name = args
        .name
        .or_else(|| cached.as_ref().map(|s| s.name.clone()))
        .or_else(|| dir.file_name().and_then(|n| n.to_str()).map(String::from))
        .ok_or_else(|| crate::error::Error::cli("Could not determine environment name"))?;

    let files = GatewayClient::scan_markdown_files(&dir)?;

    if files.is_empty() {
        eprintln!("No .md files found in {}", dir.display());
        return Ok(());
    }

    let checksums: Vec<(String, String)> = files
        .iter()
        .map(|f| (f.path.clone(), f.checksum.clone()))
        .collect();

    if let Some(ref prev) = cached {
        let same_target = prev.name == name;
        if same_target {
            let prev_map: std::collections::HashMap<&str, &str> = prev
                .checksums
                .iter()
                .map(|(k, v)| (k.as_str(), v.as_str()))
                .collect();
            let changed = checksums.len() != prev.checksums.len()
                || checksums
                    .iter()
                    .any(|(p, c)| prev_map.get(p.as_str()) != Some(&c.as_str()));

            if !changed {
                eprintln!("No changes detected, skipping sync.");
                return Ok(());
            }
        }
    }

    eprintln!(
        "Syncing {} file{} to '{name}'...",
        files.len(),
        if files.len() == 1 { "" } else { "s" }
    );

    let result = gateway.upsert_environment(&name, files).await?;

    let action = if result.created { "Created" } else { "Updated" };
    eprintln!("{action} environment '{}'", result.name);

    if let Some(ref url) = result.url {
        eprintln!("URL: {url}");
    }

    let state = SyncState::new(result.id, result.name, result.url, result.auth_token)
        .with_checksums(&checksums);

    save_state(&dir, &state)?;

    Ok(())
}
