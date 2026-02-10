use crate::error::{Error, Result};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;

const STATE_DIR: &str = ".statespace";
const STATE_FILE: &str = "state.json";

/// Local sync state stored in `.statespace/state.json` within the project directory.
/// Enables incremental deploys by caching deployment IDs and file checksums.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct SyncState {
    pub deployment_id: String,
    pub name: String,
    pub url: Option<String>,
    pub auth_token: Option<String>,
    pub last_synced: DateTime<Utc>,
    #[serde(default)]
    pub checksums: HashMap<String, String>,
}

impl SyncState {
    pub(crate) fn new(
        deployment_id: String,
        name: String,
        url: Option<String>,
        auth_token: Option<String>,
    ) -> Self {
        Self {
            deployment_id,
            name,
            url,
            auth_token,
            last_synced: Utc::now(),
            checksums: HashMap::new(),
        }
    }

    pub(crate) fn with_checksums(mut self, files: &[(String, String)]) -> Self {
        self.checksums = files.iter().cloned().collect();
        self.last_synced = Utc::now();
        self
    }
}

pub(crate) fn state_file_path(project_dir: &Path) -> std::path::PathBuf {
    project_dir.join(STATE_DIR).join(STATE_FILE)
}

fn state_dir_path(project_dir: &Path) -> std::path::PathBuf {
    project_dir.join(STATE_DIR)
}

pub(crate) fn load_state(project_dir: &Path) -> Result<Option<SyncState>> {
    let path = state_file_path(project_dir);

    if !path.exists() {
        return Ok(None);
    }

    let content = std::fs::read_to_string(&path).map_err(|e| {
        Error::cli(format!(
            "Failed to read state file '{}': {e}",
            path.display()
        ))
    })?;

    let state: SyncState = serde_json::from_str(&content).map_err(|e| {
        Error::cli(format!(
            "Failed to parse state file '{}': {e}",
            path.display()
        ))
    })?;

    Ok(Some(state))
}

pub(crate) fn save_state(project_dir: &Path, state: &SyncState) -> Result<()> {
    let dir_path = state_dir_path(project_dir);
    let file_path = state_file_path(project_dir);

    if !dir_path.exists() {
        std::fs::create_dir_all(&dir_path).map_err(|e| {
            Error::cli(format!(
                "Failed to create state directory '{}': {e}",
                dir_path.display()
            ))
        })?;
    }

    let gitignore_path = dir_path.join(".gitignore");
    if !gitignore_path.exists() {
        let _ = std::fs::write(&gitignore_path, "state.json\n");
    }

    let content = serde_json::to_string_pretty(state)
        .map_err(|e| Error::cli(format!("Failed to serialize state: {e}")))?;

    std::fs::write(&file_path, content).map_err(|e| {
        Error::cli(format!(
            "Failed to write state file '{}': {e}",
            file_path.display()
        ))
    })?;

    Ok(())
}

#[cfg(test)]
#[allow(clippy::unwrap_used)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    #[test]
    fn test_state_file_path() {
        let dir = Path::new("/projects/my-app");
        let path = state_file_path(dir);
        assert_eq!(
            path.to_string_lossy(),
            "/projects/my-app/.statespace/state.json"
        );
    }

    #[test]
    fn test_sync_state_new() {
        let state = SyncState::new(
            "abc123".to_string(),
            "my-app".to_string(),
            Some("https://example.com".to_string()),
            Some("token123".to_string()),
        );

        assert_eq!(state.deployment_id, "abc123");
        assert_eq!(state.name, "my-app");
        assert!(state.checksums.is_empty());
    }

    #[test]
    fn test_sync_state_with_checksums() {
        let state = SyncState::new("abc123".to_string(), "my-app".to_string(), None, None);

        let files = vec![
            ("README.md".to_string(), "sha256:abc".to_string()),
            ("tools/git.md".to_string(), "sha256:def".to_string()),
        ];

        let state = state.with_checksums(&files);
        assert_eq!(state.checksums.len(), 2);
        assert_eq!(
            state.checksums.get("README.md"),
            Some(&"sha256:abc".to_string())
        );
    }

    #[test]
    fn test_load_state_not_found() {
        let dir = TempDir::new().unwrap();
        let result = load_state(dir.path()).unwrap();
        assert!(result.is_none());
    }

    #[test]
    fn test_save_and_load_state() {
        let dir = TempDir::new().unwrap();

        let state = SyncState::new(
            "abc123".to_string(),
            "my-app".to_string(),
            Some("https://example.com".to_string()),
            None,
        );

        save_state(dir.path(), &state).unwrap();

        let loaded = load_state(dir.path()).unwrap().unwrap();
        assert_eq!(loaded.deployment_id, "abc123");
        assert_eq!(loaded.name, "my-app");
        assert_eq!(loaded.url, Some("https://example.com".to_string()));
    }

    #[test]
    fn test_save_creates_gitignore() {
        let dir = TempDir::new().unwrap();

        let state = SyncState::new("abc123".to_string(), "my-app".to_string(), None, None);

        save_state(dir.path(), &state).unwrap();

        let gitignore_path = dir.path().join(".statespace").join(".gitignore");
        assert!(gitignore_path.exists());

        let content = std::fs::read_to_string(gitignore_path).unwrap();
        assert!(content.contains("state.json"));
    }
}
