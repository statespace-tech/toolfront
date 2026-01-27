//! Org subcommand handlers

use crate::args::OrgCommands;
use crate::config::{load_stored_credentials, save_stored_credentials};
use crate::error::Result;
use crate::gateway::GatewayClient;
use inquire::Select;

pub(crate) async fn run(cmd: OrgCommands, gateway: GatewayClient) -> Result<()> {
    match cmd {
        OrgCommands::List => run_list(gateway).await,
        OrgCommands::Current => run_current(),
        OrgCommands::Use { org } => run_use(org, gateway).await,
    }
}

async fn run_list(gateway: GatewayClient) -> Result<()> {
    let orgs = gateway.list_organizations().await?;
    let current_org_id = load_stored_credentials()?
        .map(|c| c.org_id)
        .unwrap_or_default();

    if orgs.is_empty() {
        println!("No organizations found");
        return Ok(());
    }

    println!();
    for org in orgs {
        let marker = if org.id == current_org_id { "* " } else { "  " };
        let tier_str = org.tier.map(|t| format!(" ({t})")).unwrap_or_default();
        println!("{marker}{}{tier_str}", org.name);
    }
    println!();

    Ok(())
}

fn run_current() -> Result<()> {
    let Some(creds) = load_stored_credentials()? else {
        println!("Not logged in. Run `statespace auth login` first.");
        return Ok(());
    };

    if creds.org_id.is_empty() {
        println!("No organization selected");
        return Ok(());
    }

    let display = creds.org_name.unwrap_or_else(|| creds.org_id.clone());
    println!("{display}");

    Ok(())
}

async fn run_use(org: Option<String>, gateway: GatewayClient) -> Result<()> {
    let Some(mut creds) = load_stored_credentials()? else {
        return Err(crate::error::Error::cli(
            "Not logged in. Run `statespace auth login` first.",
        ));
    };

    let orgs = gateway.list_organizations().await?;

    if orgs.is_empty() {
        return Err(crate::error::Error::cli("No organizations available"));
    }

    let selected = match org {
        Some(query) => {
            let query_lower = query.to_lowercase();
            orgs.iter()
                .find(|o| o.id == query || o.name.to_lowercase().contains(&query_lower))
                .ok_or_else(|| {
                    crate::error::Error::cli(format!("Organization not found: {query}"))
                })?
                .clone()
        }
        None => {
            let org_names: Vec<&str> = orgs.iter().map(|o| o.name.as_str()).collect();
            let selection = Select::new("Select organization:", org_names)
                .with_vim_mode(true)
                .prompt()
                .map_err(|e| crate::error::Error::cli(format!("Selection cancelled: {e}")))?;

            orgs.iter()
                .find(|o| o.name == selection)
                .ok_or_else(|| crate::error::Error::cli("Organization not found"))?
                .clone()
        }
    };

    creds.org_id = selected.id;
    creds.org_name = Some(selected.name.clone());
    save_stored_credentials(&creds)?;

    println!("Switched to organization: {}", selected.name);

    Ok(())
}
