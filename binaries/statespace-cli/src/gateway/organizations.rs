use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct Organization {
    pub id: String,
    pub name: String,
    pub tier: Option<String>,
}
