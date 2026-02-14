use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
#[allow(dead_code)]
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

#[derive(Debug, Clone, Deserialize)]
#[allow(dead_code)]
pub(crate) struct TokenCreateResult {
    pub id: String,
    pub name: String,
    pub scope: String,
    pub token: String,
    pub created_at: String,
    pub expires_at: Option<String>,
}
