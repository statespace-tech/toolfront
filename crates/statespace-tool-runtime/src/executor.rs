//! Tool execution with sandboxing and resource limits.

use crate::error::Error;
use crate::security::{is_private_or_restricted_ip, validate_url_initial};
use crate::tools::{BuiltinTool, HttpMethod};
use std::path::PathBuf;
use std::time::Duration;
use tokio::process::Command;
use tokio::time::timeout;
use tracing::{info, instrument, warn};

#[derive(Debug, Clone)]
pub struct ExecutionLimits {
    pub max_output_bytes: usize,
    pub max_list_items: usize,
    pub timeout: Duration,
}

impl Default for ExecutionLimits {
    fn default() -> Self {
        Self {
            max_output_bytes: 1024 * 1024, // 1MB
            max_list_items: 1000,
            timeout: Duration::from_secs(30),
        }
    }
}

#[derive(Debug, Clone)]
#[non_exhaustive]
pub enum ToolOutput {
    Text(String),
    FileList(Vec<FileInfo>),
}

impl ToolOutput {
    #[must_use]
    pub fn to_text(&self) -> String {
        match self {
            Self::Text(s) => s.clone(),
            Self::FileList(files) => files
                .iter()
                .map(|f| f.key.as_str())
                .collect::<Vec<_>>()
                .join("\n"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct FileInfo {
    pub key: String,
    pub size: u64,
    pub last_modified: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug)]
pub struct ToolExecutor {
    root: PathBuf,
    limits: ExecutionLimits,
}

impl ToolExecutor {
    #[must_use]
    pub const fn new(root: PathBuf, limits: ExecutionLimits) -> Self {
        Self { root, limits }
    }

    /// # Errors
    ///
    /// Returns errors for timeouts, invalid commands, or execution failures.
    #[instrument(skip(self), fields(tool = ?tool))]
    pub async fn execute(&self, tool: &BuiltinTool) -> Result<ToolOutput, Error> {
        let execution = async {
            match tool {
                BuiltinTool::Glob { pattern } => self.execute_glob(pattern),
                BuiltinTool::Curl { url, method } => self.execute_curl(url, *method).await,
                BuiltinTool::Exec { command, args } => self.execute_exec(command, args).await,
            }
        };

        timeout(self.limits.timeout, execution)
            .await
            .map_err(|_err| Error::Timeout)?
    }

    async fn execute_exec(&self, command: &str, args: &[String]) -> Result<ToolOutput, Error> {
        info!("Executing: {} {:?}", command, args);

        for arg in args {
            if arg.starts_with('/') {
                return Err(Error::Security(format!(
                    "Absolute paths not allowed in command arguments: {arg}"
                )));
            }
            if arg.contains("..") {
                return Err(Error::Security(format!(
                    "Path traversal not allowed in command arguments: {arg}"
                )));
            }
        }

        let output = Command::new(command)
            .args(args)
            .current_dir(&self.root)
            .env_clear()
            .env("PATH", "/usr/local/bin:/usr/bin:/bin")
            .env("HOME", "/tmp")
            .env("LANG", "C.UTF-8")
            .env("LC_ALL", "C.UTF-8")
            .output()
            .await
            .map_err(|e| Error::Internal(format!("Failed to execute {command}: {e}")))?;

        let mut result = String::from_utf8_lossy(&output.stdout).into_owned();
        if !output.stderr.is_empty() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            if !result.is_empty() {
                result.push('\n');
            }
            result.push_str(&stderr);
        }

        if result.len() > self.limits.max_output_bytes {
            return Err(Error::OutputTooLarge {
                size: result.len(),
                limit: self.limits.max_output_bytes,
            });
        }

        Ok(ToolOutput::Text(result))
    }

    fn execute_glob(&self, pattern: &str) -> Result<ToolOutput, Error> {
        let full_pattern = self.safe_join(pattern)?;
        info!("Executing glob: {:?}", full_pattern);

        let pattern_str = full_pattern
            .to_str()
            .ok_or_else(|| Error::Internal("Invalid UTF-8 path".to_string()))?;

        let paths = glob::glob(pattern_str)
            .map_err(|e| Error::InvalidCommand(format!("Invalid glob: {e}")))?;

        let mut files = Vec::new();
        for entry in paths {
            match entry {
                Ok(path) => {
                    let relative = path
                        .strip_prefix(&self.root)
                        .unwrap_or(&path)
                        .to_string_lossy()
                        .into_owned();

                    let metadata = std::fs::metadata(&path).ok();
                    let size = metadata.as_ref().map_or(0, std::fs::Metadata::len);
                    let last_modified = metadata
                        .and_then(|m| m.modified().ok())
                        .map_or_else(chrono::Utc::now, chrono::DateTime::<chrono::Utc>::from);

                    files.push(FileInfo {
                        key: relative,
                        size,
                        last_modified,
                    });
                }
                Err(e) => warn!("Glob error: {}", e),
            }
        }

        if files.len() > self.limits.max_list_items {
            files.truncate(self.limits.max_list_items);
        }

        Ok(ToolOutput::FileList(files))
    }

    async fn execute_curl(&self, url: &str, method: HttpMethod) -> Result<ToolOutput, Error> {
        let parsed = validate_url_initial(url)?;
        let host = parsed
            .host_str()
            .ok_or_else(|| Error::InvalidCommand("URL has no host".to_string()))?;
        let port = parsed
            .port_or_known_default()
            .ok_or_else(|| Error::InvalidCommand("Could not determine port".to_string()))?;

        info!("Executing curl: {} {}", method, host);

        let addr_str = format!("{host}:{port}");
        let addrs = tokio::net::lookup_host(&addr_str)
            .await
            .map_err(|e| Error::Network(format!("DNS resolution failed: {e}")))?;

        for addr in addrs {
            if is_private_or_restricted_ip(&addr.ip()) {
                return Err(Error::Security(format!(
                    "Access to private IP blocked: {}",
                    addr.ip()
                )));
            }
        }

        let client = reqwest::Client::builder()
            .timeout(self.limits.timeout)
            .user_agent("Statespace/1.0")
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .map_err(|e| Error::Network(format!("Client error: {e}")))?;

        let http_method = reqwest::Method::from_bytes(method.as_str().as_bytes())
            .map_err(|_e| Error::InvalidCommand(format!("Invalid HTTP method: {method}")))?;

        let response = client
            .request(http_method, parsed.as_str())
            .send()
            .await
            .map_err(|e| Error::Network(format!("Request failed: {e}")))?;

        let text = response
            .text()
            .await
            .map_err(|e| Error::Network(format!("Read failed: {e}")))?;

        if text.len() > self.limits.max_output_bytes {
            return Err(Error::OutputTooLarge {
                size: text.len(),
                limit: self.limits.max_output_bytes,
            });
        }

        Ok(ToolOutput::Text(text))
    }

    fn safe_join(&self, path: &str) -> Result<PathBuf, Error> {
        let path = path.trim_start_matches('/');
        if path.contains("..") {
            return Err(Error::PathTraversal {
                attempted: path.to_string(),
                boundary: self.root.to_string_lossy().to_string(),
            });
        }
        Ok(self.root.join(path))
    }

    #[must_use]
    pub const fn limits(&self) -> &ExecutionLimits {
        &self.limits
    }

    #[must_use]
    pub fn root(&self) -> &PathBuf {
        &self.root
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_executor() -> ToolExecutor {
        ToolExecutor::new(PathBuf::from("/tmp/test-mount"), ExecutionLimits::default())
    }

    #[tokio::test]
    async fn exec_rejects_absolute_paths() {
        let executor = test_executor();
        let tool = BuiltinTool::Exec {
            command: "grep".to_string(),
            args: vec!["pattern".to_string(), "/etc/passwd".to_string()],
        };

        let result = executor.execute(&tool).await;
        assert!(matches!(result, Err(Error::Security(_))));
    }

    #[tokio::test]
    async fn exec_rejects_path_traversal() {
        let executor = test_executor();
        let tool = BuiltinTool::Exec {
            command: "cat".to_string(),
            args: vec!["../../../etc/passwd".to_string()],
        };

        let result = executor.execute(&tool).await;
        assert!(matches!(result, Err(Error::Security(_))));
    }

    #[tokio::test]
    async fn exec_allows_relative_paths() {
        let executor = test_executor();
        let tool = BuiltinTool::Exec {
            command: "ls".to_string(),
            args: vec!["-la".to_string(), "subdir/file.txt".to_string()],
        };

        let result = executor.execute(&tool).await;
        assert!(!matches!(result, Err(Error::Security(_))));
    }
}
