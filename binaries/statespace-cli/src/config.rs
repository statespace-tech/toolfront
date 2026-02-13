use crate::error::{ConfigError, Result};
use crate::gateway::{AuthorizedUser, ExchangeTokenResponse};
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
        dirs::home_dir().map_or_else(|| PathBuf::from("."), |h| h.join("AppData").join("Roaming"))
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

pub(crate) fn resolve_credentials(
    cli_api_key: Option<&str>,
    cli_org_id: Option<&str>,
) -> Result<Credentials> {
    let stored = load_stored_credentials().ok().flatten();
    let stored_key = stored.as_ref().and_then(|c| {
        if c.api_key.is_empty() {
            None
        } else {
            Some(c.api_key.clone())
        }
    });
    let stored_org = stored.as_ref().and_then(|c| {
        if c.org_id.is_empty() {
            None
        } else {
            Some(c.org_id.clone())
        }
    });
    let stored_url = stored.as_ref().map(|c| c.api_url.clone());

    let config = load_config_file();
    let context = config.as_ref().and_then(get_current_context);

    let cfg_url = context.and_then(|c| c.api_url.clone());
    let cfg_key = context.and_then(|c| c.api_key.clone());
    let cfg_org = context.and_then(|c| c.org_id.clone());

    let api_url = stored_url
        .or(cfg_url)
        .unwrap_or_else(|| DEFAULT_API_URL.to_string());

    let api_key = cli_api_key
        .map(String::from)
        .or(stored_key)
        .or(cfg_key)
        .ok_or_else(|| ConfigError::MissingApiKey {
            config_path: config_path().display().to_string(),
        })?;

    let org_id = cli_org_id.map(String::from).or(stored_org).or(cfg_org);

    Ok(Credentials {
        api_url,
        api_key,
        org_id,
    })
}

pub(crate) fn resolve_api_url() -> String {
    let stored = load_stored_credentials().ok().flatten();
    let stored_url = stored.as_ref().map(|c| c.api_url.clone());

    let config = load_config_file();
    let context = config.as_ref().and_then(get_current_context);
    let cfg_url = context.and_then(|c| c.api_url.clone());

    stored_url
        .or(cfg_url)
        .unwrap_or_else(|| DEFAULT_API_URL.to_string())
}

pub(crate) fn credentials_path() -> PathBuf {
    config_dir().join("credentials.json")
}

fn config_dir() -> PathBuf {
    if let Ok(xdg) = std::env::var("XDG_CONFIG_HOME") {
        return PathBuf::from(xdg).join("statespace");
    }

    let base = if cfg!(target_os = "windows") {
        dirs::home_dir().map_or_else(|| PathBuf::from("."), |h| h.join("AppData").join("Roaming"))
    } else {
        dirs::home_dir().map_or_else(|| PathBuf::from("."), |h| h.join(".config"))
    };
    base.join("statespace")
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct StoredCredentials {
    pub api_key: String,
    pub org_id: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub org_name: Option<String>,
    pub email: String,
    pub name: Option<String>,
    pub user_id: String,
    pub expires_at: Option<String>,
    pub api_url: String,
}

impl StoredCredentials {
    pub(crate) fn from_exchange(
        user: AuthorizedUser,
        exchange: ExchangeTokenResponse,
        api_url: String,
    ) -> Self {
        Self {
            api_key: exchange.api_key,
            org_id: exchange.organization_id,
            org_name: None,
            email: user.email,
            name: user.name,
            user_id: user.user_id,
            expires_at: exchange.expires_at,
            api_url,
        }
    }
}

pub(crate) fn load_stored_credentials() -> Result<Option<StoredCredentials>> {
    let path = credentials_path();
    if !path.exists() {
        return Ok(None);
    }

    let content = std::fs::read_to_string(&path)
        .map_err(|e| ConfigError::Invalid(format!("Failed to read credentials: {e}")))?;

    let creds: StoredCredentials = serde_json::from_str(&content)
        .map_err(|e| ConfigError::Invalid(format!("Failed to parse credentials: {e}")))?;

    Ok(Some(creds))
}

pub(crate) fn save_stored_credentials(creds: &StoredCredentials) -> Result<()> {
    let dir = config_dir();
    if !dir.exists() {
        std::fs::create_dir_all(&dir)
            .map_err(|e| ConfigError::Invalid(format!("Failed to create config directory: {e}")))?;
    }

    let path = credentials_path();
    let content = serde_json::to_string_pretty(creds)
        .map_err(|e| ConfigError::Invalid(format!("Failed to serialize credentials: {e}")))?;

    std::fs::write(&path, content)
        .map_err(|e| ConfigError::Invalid(format!("Failed to write credentials: {e}")))?;

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
        std::fs::remove_file(&path)
            .map_err(|e| ConfigError::Invalid(format!("Failed to delete credentials: {e}")))?;
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
