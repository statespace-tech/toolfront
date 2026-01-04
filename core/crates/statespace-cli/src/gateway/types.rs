//! API types for the Statespace gateway

use serde::{Deserialize, Serialize};

/// A file to be deployed as part of an environment
#[derive(Debug, Clone, Serialize)]
pub(crate) struct EnvironmentFile {
    pub path: String,
    pub content: String,
    pub checksum: String,
}

/// Result of deploying a new environment
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct DeployResult {
    pub id: String,
    pub auth_token: Option<String>,
    pub url: Option<String>,
    pub fly_url: Option<String>,
}

/// A deployed environment/app
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct Environment {
    pub id: String,
    pub name: String,
    pub status: String,
    pub url: Option<String>,
    #[allow(dead_code)]
    pub fly_url: Option<String>,
    #[allow(dead_code)]
    pub created_at: String,
}

/// A personal access token
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct Token {
    pub id: String,
    pub name: String,
    pub scope: String,
    pub created_at: String,
    #[serde(default)]
    pub is_active: bool,
    pub expires_at: Option<String>,
    pub last_used_at: Option<String>,
    #[serde(default)]
    pub usage_count: u64,
    pub allowed_environments: Option<Vec<String>>,
    pub revoked_at: Option<String>,
    pub revoked_by: Option<String>,
    pub revocation_reason: Option<String>,
}

/// Result of creating or rotating a token
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct TokenCreateResult {
    pub id: String,
    pub name: String,
    pub scope: String,
    pub token: String,
    pub created_at: String,
    pub expires_at: Option<String>,
}
