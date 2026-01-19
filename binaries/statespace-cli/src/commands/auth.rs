//! Auth subcommand handlers implementing RFC 8628 device authorization flow.

use crate::args::{AuthCommands, TokenOutputFormat};
use crate::config::{
    credentials_path, delete_stored_credentials, load_stored_credentials, save_stored_credentials,
    StoredCredentials,
};
use crate::error::Result;
use crate::gateway::{AuthClient, DeviceTokenResponse};
use std::io::{self, Write};
use std::time::Duration;

const DEFAULT_API_URL: &str = "https://api.statespace.com";

pub(crate) async fn run(cmd: AuthCommands, api_url: Option<&str>) -> Result<()> {
    match cmd {
        AuthCommands::Login => run_login(api_url).await,
        AuthCommands::Logout => run_logout(),
        AuthCommands::Status => run_status(),
        AuthCommands::Token { format } => run_token(format),
    }
}

async fn run_login(api_url: Option<&str>) -> Result<()> {
    let api_url = api_url.unwrap_or(DEFAULT_API_URL);

    if let Some(creds) = load_stored_credentials()? {
        println!("Already logged in as {}", creds.email);
        print!("Log out and re-authenticate? [y/N] ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;

        if !input.trim().eq_ignore_ascii_case("y") {
            println!("Cancelled");
            return Ok(());
        }

        delete_stored_credentials()?;
    }

    let client = AuthClient::with_url(api_url)?;

    println!("Requesting authorization...");
    let device_code = client.request_device_code().await?;

    println!();
    println!("Open this URL in your browser:");
    println!();
    println!("  {}", device_code.verification_url);
    println!();
    println!("And enter code: {}", device_code.user_code);
    println!();

    if open::that(&device_code.verification_url).is_ok() {
        println!("Browser opened automatically.");
    }

    println!("Waiting for authorization...");

    let interval = Duration::from_secs(device_code.interval);
    let timeout = Duration::from_secs(device_code.expires_in);
    let start = std::time::Instant::now();

    loop {
        if start.elapsed() > timeout {
            return Err(crate::error::Error::cli(
                "Authorization timed out. Please try again.",
            ));
        }

        tokio::time::sleep(interval).await;

        match client.poll_device_token(&device_code.device_code).await? {
            DeviceTokenResponse::Pending => {
                print!(".");
                io::stdout().flush()?;
            }
            DeviceTokenResponse::Authorized(user) => {
                println!();
                println!();

                // Exchange JWT for CLI API key
                println!("Exchanging token for API key...");
                let exchange_result = client.exchange_token(&user.access_token).await?;

                let creds = StoredCredentials::from_exchange(
                    user,
                    exchange_result,
                    api_url.to_string(),
                );
                save_stored_credentials(&creds)?;

                println!("✓ Logged in as {}", creds.email);
                println!();
                println!("Credentials saved to {}", credentials_path().display());

                return Ok(());
            }
            DeviceTokenResponse::Expired => {
                println!();
                return Err(crate::error::Error::cli(
                    "Authorization expired or was denied. Please try again.",
                ));
            }
        }
    }
}

fn run_logout() -> Result<()> {
    match load_stored_credentials()? {
        Some(creds) => {
            delete_stored_credentials()?;
            println!("✓ Logged out (was {})", creds.email);
        }
        None => {
            println!("Not currently logged in");
        }
    }
    Ok(())
}

fn run_status() -> Result<()> {
    if let Some(creds) = load_stored_credentials()? {
        println!("Logged in as: {}", creds.email);
        if let Some(name) = &creds.name {
            println!("Name:         {name}");
        }
        println!("User ID:      {}", creds.user_id);
        println!("API URL:      {}", creds.api_url);
        if let Some(expires) = &creds.expires_at {
            println!("Expires:      {expires}");
        }
        println!();
        println!("Credentials:  {}", credentials_path().display());
    } else {
        println!("Not logged in");
        println!();
        println!("Run `statespace auth login` to authenticate.");
    }
    Ok(())
}

fn run_token(format: TokenOutputFormat) -> Result<()> {
    let Some(creds) = load_stored_credentials()? else {
        eprintln!("Not logged in. Run `statespace auth login` first.");
        std::process::exit(1);
    };

    match format {
        TokenOutputFormat::Plain => {
            println!("{}", creds.api_key);
        }
        TokenOutputFormat::Json => {
            let output = serde_json::json!({
                "api_key": creds.api_key,
                "org_id": creds.org_id,
                "email": creds.email,
                "user_id": creds.user_id,
                "expires_at": creds.expires_at,
            });
            println!("{}", serde_json::to_string_pretty(&output).unwrap_or_default());
        }
    }
    Ok(())
}
