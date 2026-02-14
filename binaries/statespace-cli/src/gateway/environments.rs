use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize)]
pub(crate) struct EnvironmentFile {
    pub path: String,
    pub content: String,
    pub checksum: String,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct DeployResult {
    pub id: String,
    pub auth_token: Option<String>,
    pub url: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct UpsertResult {
    pub created: bool,
    pub id: String,
    pub name: String,
    pub url: Option<String>,
    pub auth_token: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
#[allow(dead_code)]
pub(crate) struct Environment {
    pub id: String,
    pub name: String,
    pub status: String,
    pub url: Option<String>,
    pub created_at: String,
    pub auth_token: Option<String>,
}
