use crate::args::{
    TokenCreateArgs, TokenGetArgs, TokenListArgs, TokenRevokeArgs, TokenRotateArgs, TokensCommands,
};
use crate::error::Result;
use crate::gateway::GatewayClient;
use chrono::{DateTime, Utc};
use std::io::{self, Write};

pub(crate) async fn run(cmd: TokensCommands, gateway: GatewayClient) -> Result<()> {
    match cmd {
        TokensCommands::Create(args) => run_create(args, gateway).await,
        TokensCommands::List(args) => run_list(args, gateway).await,
        TokensCommands::Get(args) => run_get(args, gateway).await,
        TokensCommands::Rotate(args) => run_rotate(args, gateway).await,
        TokensCommands::Revoke(args) => run_revoke(args, gateway).await,
    }
}

async fn run_create(args: TokenCreateArgs, gateway: GatewayClient) -> Result<()> {
    eprintln!("Creating token '{}'...", args.name);

    let app_ids = if args.app_ids.is_empty() {
        None
    } else {
        Some(args.app_ids.as_slice())
    };

    let result = gateway
        .create_token(&args.name, &args.scope, app_ids, args.expires.as_deref())
        .await?;

    println!();
    println!("{}", "=".repeat(80));
    print_kv("Token ID:", &result.id);
    print_kv("Name:", &result.name);
    print_kv("Scope:", &result.scope);
    print_kv("Created:", &result.created_at);
    if let Some(expires) = &result.expires_at {
        print_kv("Expires:", expires);
    }
    println!();
    println!("{}", "─".repeat(80));
    println!("  Token (save this — shown only once):");
    println!("  {}", result.token);
    println!("{}", "=".repeat(80));
    eprintln!("\n✓ Token created");

    Ok(())
}

async fn run_list(args: TokenListArgs, gateway: GatewayClient) -> Result<()> {
    let tokens = gateway.list_tokens(!args.all, args.limit, 0).await?;

    if tokens.is_empty() {
        println!("No tokens found.");
        return Ok(());
    }

    eprintln!("{} token(s)\n", tokens.len());

    for token in tokens {
        let status = if token.is_active { "✓" } else { "✗" };
        let scope = token.scope.replace("environments:", "");
        let time_ago = format_relative_time(&token.created_at);
        let short_id = if token.id.len() > 12 {
            &token.id[token.id.len() - 12..]
        } else {
            &token.id
        };

        println!("{status} {}", token.name);
        println!("  {scope} • {time_ago} • {short_id}");

        if token.usage_count > 0 {
            let last_used = token
                .last_used_at
                .as_deref()
                .map_or_else(|| "never".to_string(), format_relative_time);
            println!("  Used {} time(s), last: {last_used}", token.usage_count);
        }
        println!();
    }

    Ok(())
}

async fn run_get(args: TokenGetArgs, gateway: GatewayClient) -> Result<()> {
    let token = gateway.get_token(&args.token_id).await?;

    let status = if token.is_active { "active" } else { "revoked" };

    println!();
    println!("{}", "=".repeat(80));
    print_kv("ID:", &token.id);
    print_kv("Name:", &token.name);
    print_kv("Scope:", &token.scope);
    print_kv("Status:", status);
    print_kv("Created:", &token.created_at);
    if let Some(expires) = &token.expires_at {
        print_kv("Expires:", expires);
    }
    if let Some(last_used) = &token.last_used_at {
        print_kv("Last used:", last_used);
    }
    print_kv("Usage count:", &token.usage_count.to_string());

    if let Some(envs) = &token.allowed_environments {
        let env_str = if envs.is_empty() {
            "All".to_string()
        } else {
            envs.join(", ")
        };
        print_kv("Allowed apps:", &env_str);
    }

    if let Some(revoked_at) = &token.revoked_at {
        print_kv("Revoked:", revoked_at);
        if let Some(by) = &token.revoked_by {
            print_kv("Revoked by:", by);
        }
        if let Some(reason) = &token.revocation_reason {
            print_kv("Reason:", reason);
        }
    }
    println!("{}", "=".repeat(80));

    Ok(())
}

async fn run_rotate(args: TokenRotateArgs, gateway: GatewayClient) -> Result<()> {
    eprintln!("Rotating token {}...", args.token_id);

    let app_ids = if args.app_ids.is_empty() {
        None
    } else {
        Some(args.app_ids.as_slice())
    };

    let result = gateway
        .rotate_token(
            &args.token_id,
            args.name.as_deref(),
            args.scope.as_deref(),
            app_ids,
            args.expires.as_deref(),
        )
        .await?;

    println!();
    println!("{}", "=".repeat(80));
    print_kv("Token ID:", &result.id);
    print_kv("Name:", &result.name);
    print_kv("Scope:", &result.scope);
    println!();
    println!("{}", "─".repeat(80));
    println!("  New Token (save this — shown only once):");
    println!("  {}", result.token);
    println!("{}", "=".repeat(80));
    eprintln!("\n✓ Token rotated (old token revoked)");

    Ok(())
}

async fn run_revoke(args: TokenRevokeArgs, gateway: GatewayClient) -> Result<()> {
    if !args.yes {
        eprint!("Revoke token {}? [y/N] ", args.token_id);
        io::stderr().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)?;

        if !input.trim().eq_ignore_ascii_case("y") {
            eprintln!("Cancelled.");
            return Ok(());
        }
    }

    gateway
        .revoke_token(&args.token_id, args.reason.as_deref())
        .await?;
    eprintln!("✓ Token revoked");

    Ok(())
}

fn print_kv(key: &str, value: &str) {
    println!("  {key:<16} {value}");
}

fn format_relative_time(iso: &str) -> String {
    let Ok(dt) = DateTime::parse_from_rfc3339(iso) else {
        return iso.to_string();
    };

    let now = Utc::now();
    let delta = now.signed_duration_since(dt.with_timezone(&Utc));

    if delta.num_days() > 0 {
        format!("{}d ago", delta.num_days())
    } else if delta.num_hours() > 0 {
        format!("{}h ago", delta.num_hours())
    } else if delta.num_minutes() > 0 {
        format!("{}m ago", delta.num_minutes())
    } else {
        "just now".to_string()
    }
}
