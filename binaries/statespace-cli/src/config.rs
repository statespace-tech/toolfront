//! Configuration and credential resolution.
//!
//! Precedence: CLI flags > config file > environment variables > defaults.

use crate::error::{ConfigError, Result};
use crate::gateway::AuthorizedUser;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

const DEFAULT_API_URL: &str = "https://api.statespace.com";

#[derive(Debug, Deserialize)]
struct ConfigFile {
    current_context: Option<String>,
    contexts: Option<HashMap<String, Context>>,
}

#[derive(Debug, Deserialize)]
struct Context {
    api_url: Option<String>,
    api_key: Option<String>,
    org_id: Option<String>,
}

#[derive(Debug, Clone)]
pub(crate) struct Credentials {
    pub api_url: String,
    pub api_key: String,
    pub org_id: Option<String>,
}

pub(crate) fn config_path() -> PathBuf {
    if let Ok(xdg) = std::env::var("XDG_CONFIG_HOME") {
        return PathBuf::from(xdg).join("statespace").join("config.toml");
    }

    let base = if cfg!(target_os = "windows") {
        dirs::home_dir().map_or_else(
            || PathBuf::from("."),
            |h| h.join("AppData").join("Roaming"),
        )
    } else {
        dirs::home_dir().map_or_else(|| PathBuf::from("."), |h| h.join(".config"))
    };
    base.join("statespace").join("config.toml")
}

fn load_config_file() -> Option<ConfigFile> {
    let path = config_path();
    if !path.exists() {
        return None;
    }
    let content = std::fs::read_to_string(&path).ok()?;
    toml::from_str(&content).ok()
}

fn get_current_context(config: &ConfigFile) -> Option<&Context> {
    let name = config.current_context.as_ref()?;
    config.contexts.as_ref()?.get(name)
}

fn env_var(statespace_key: &str, toolfront_key: &str) -> Option<String> {
    std::env::var(statespace_key)
        .ok()
        .or_else(|| std::env::var(toolfront_key).ok())
}

pub(crate) fn resolve_credentials(
    cli_api_url: Option<&str>,
    cli_api_key: Option<&str>,
    cli_org_id: Option<&str>,
) -> Result<Credentials> {
    let config = load_config_file();
    let context = config.as_ref().and_then(get_current_context);

    let cfg_url = context.and_then(|c| c.api_url.clone());
    let cfg_key = context.and_then(|c| c.api_key.clone());
    let cfg_org = context.and_then(|c| c.org_id.clone());

    let env_url = env_var("STATESPACE_API_URL", "TOOLFRONT_GATEWAY_URL");
    let env_key = env_var("STATESPACE_API_KEY", "TOOLFRONT_API_KEY");
    let env_org = env_var("STATESPACE_ORG_ID", "TOOLFRONT_ORG_ID");

    let api_url = cli_api_url
        .map(String::from)
        .or(cfg_url)
        .or(env_url)
        .unwrap_or_else(|| DEFAULT_API_URL.to_string());

    let api_key = cli_api_key
        .map(String::from)
        .or(cfg_key)
        .or(env_key)
        .ok_or_else(|| ConfigError::MissingApiKey {
            config_path: config_path().display().to_string(),
        })?;

    let org_id = cli_org_id.map(String::from).or(cfg_org).or(env_org);

    Ok(Credentials {
        api_url,
        api_key,
        org_id,
    })
}

pub(crate) fn credentials_path() -> PathBuf {
    config_dir().join("credentials.json")
}

fn config_dir() -> PathBuf {
    if let Ok(xdg) = std::env::var("XDG_CONFIG_HOME") {
        return PathBuf::from(xdg).join("statespace");
    }

    let base = if cfg!(target_os = "windows") {
        dirs::home_dir().map_or_else(
            || PathBuf::from("."),
            |h| h.join("AppData").join("Roaming"),
        )
    } else {
        dirs::home_dir().map_or_else(|| PathBuf::from("."), |h| h.join(".config"))
    };
    base.join("statespace")
}

/// Credentials stored locally after `auth login`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct StoredCredentials {
    pub access_token: String,
    pub email: String,
    pub name: Option<String>,
    pub user_id: String,
    pub expires_at: Option<String>,
    pub api_url: String,
}

impl StoredCredentials {
    pub(crate) fn from_auth(user: AuthorizedUser, api_url: String) -> Self {
        Self {
            access_token: user.access_token,
            email: user.email,
            name: user.name,
            user_id: user.user_id,
            expires_at: user.expires_at,
            api_url,
        }
    }
}

pub(crate) fn load_stored_credentials() -> Result<Option<StoredCredentials>> {
    let path = credentials_path();
    if !path.exists() {
        return Ok(None);
    }

    let content = std::fs::read_to_string(&path).map_err(|e| {
        ConfigError::Invalid(format!("Failed to read credentials: {e}"))
    })?;

    let creds: StoredCredentials = serde_json::from_str(&content).map_err(|e| {
        ConfigError::Invalid(format!("Failed to parse credentials: {e}"))
    })?;

    Ok(Some(creds))
}

pub(crate) fn save_stored_credentials(creds: &StoredCredentials) -> Result<()> {
    let dir = config_dir();
    if !dir.exists() {
        std::fs::create_dir_all(&dir).map_err(|e| {
            ConfigError::Invalid(format!("Failed to create config directory: {e}"))
        })?;
    }

    let path = credentials_path();
    let content = serde_json::to_string_pretty(creds).map_err(|e| {
        ConfigError::Invalid(format!("Failed to serialize credentials: {e}"))
    })?;

    std::fs::write(&path, content).map_err(|e| {
        ConfigError::Invalid(format!("Failed to write credentials: {e}"))
    })?;

    // Set restrictive permissions on Unix
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let perms = std::fs::Permissions::from_mode(0o600);
        let _ = std::fs::set_permissions(&path, perms);
    }

    Ok(())
}

pub(crate) fn delete_stored_credentials() -> Result<()> {
    let path = credentials_path();
    if path.exists() {
        std::fs::remove_file(&path).map_err(|e| {
            ConfigError::Invalid(format!("Failed to delete credentials: {e}"))
        })?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_path_exists() {
        let path = config_path();
        assert!(path.to_string_lossy().contains("statespace"));
        assert!(path.to_string_lossy().ends_with("config.toml"));
    }

    #[test]
    fn test_credentials_path() {
        let path = credentials_path();
        assert!(path.to_string_lossy().contains("statespace"));
        assert!(path.to_string_lossy().ends_with("credentials.json"));
    }
}
