//! Content resolution from a content root directory.

use async_trait::async_trait;
use statespace_tool_runtime::Error;
use std::path::{Path, PathBuf};
use tokio::fs;

#[async_trait]
pub trait ContentResolver: Send + Sync {
    async fn resolve(&self, path: &str) -> Result<String, Error>;
    async fn resolve_path(&self, path: &str) -> Result<PathBuf, Error>;
}

#[derive(Debug)]
pub struct LocalContentResolver {
    root: PathBuf,
}

impl LocalContentResolver {
    /// # Errors
    ///
    /// Returns an error if the root path cannot be canonicalized.
    pub fn new(root: &Path) -> Result<Self, Error> {
        let root = root.canonicalize().map_err(|e| {
            Error::Io(std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                format!("Failed to canonicalize root path: {e}"),
            ))
        })?;
        Ok(Self { root })
    }

    #[must_use]
    pub fn root(&self) -> &Path {
        &self.root
    }

    fn validate_path(&self, requested: &str) -> Result<PathBuf, Error> {
        let requested = requested.trim_start_matches('/');

        if requested.contains("..") {
            return Err(Error::PathTraversal {
                attempted: requested.to_string(),
                boundary: self.root.to_string_lossy().to_string(),
            });
        }

        let target = if requested.is_empty() {
            self.root.clone()
        } else {
            self.root.join(requested)
        };

        Ok(target)
    }

    fn resolve_to_file(target: &Path, original: &str) -> Result<PathBuf, Error> {
        if target.is_file() {
            return Ok(target.to_path_buf());
        }

        if target.is_dir() {
            let readme = target.join("README.md");
            if readme.is_file() {
                return Ok(readme);
            }
            return Err(Error::NotFound(original.to_string()));
        }

        let mut with_md = target.to_path_buf();
        with_md.set_extension("md");
        if with_md.is_file() {
            return Ok(with_md);
        }

        Err(Error::NotFound(original.to_string()))
    }
}

#[async_trait]
impl ContentResolver for LocalContentResolver {
    async fn resolve(&self, path: &str) -> Result<String, Error> {
        let target = self.validate_path(path)?;
        let resolved = Self::resolve_to_file(&target, path)?;

        let resolved = resolved
            .canonicalize()
            .map_err(|_err| Error::NotFound(path.to_string()))?;
        if !resolved.starts_with(&self.root) {
            return Err(Error::PathTraversal {
                attempted: path.to_string(),
                boundary: self.root.to_string_lossy().to_string(),
            });
        }

        fs::read_to_string(&resolved).await.map_err(Error::Io)
    }

    async fn resolve_path(&self, path: &str) -> Result<PathBuf, Error> {
        let target = self.validate_path(path)?;
        let resolved = Self::resolve_to_file(&target, path)?;

        let resolved = resolved
            .canonicalize()
            .map_err(|_err| Error::NotFound(path.to_string()))?;
        if !resolved.starts_with(&self.root) {
            return Err(Error::PathTraversal {
                attempted: path.to_string(),
                boundary: self.root.to_string_lossy().to_string(),
            });
        }

        Ok(resolved)
    }
}

#[cfg(test)]
#[allow(clippy::unwrap_used)]
mod tests {
    use super::*;
    use std::fs::write;
    use tempfile::TempDir;

    fn setup_test_dir() -> TempDir {
        let dir = TempDir::new().unwrap();
        write(dir.path().join("README.md"), "# Root README").unwrap();
        write(dir.path().join("file.md"), "# File").unwrap();
        std::fs::create_dir(dir.path().join("subdir")).unwrap();
        write(dir.path().join("subdir/README.md"), "# Subdir README").unwrap();
        dir
    }

    #[tokio::test]
    async fn test_resolve_root_readme() {
        let dir = setup_test_dir();
        let resolver = LocalContentResolver::new(dir.path()).unwrap();

        let content = resolver.resolve("").await.unwrap();
        assert!(content.contains("# Root README"));
    }

    #[tokio::test]
    async fn test_resolve_file() {
        let dir = setup_test_dir();
        let resolver = LocalContentResolver::new(dir.path()).unwrap();

        let content = resolver.resolve("file.md").await.unwrap();
        assert!(content.contains("# File"));
    }

    #[tokio::test]
    async fn test_resolve_file_without_extension() {
        let dir = setup_test_dir();
        let resolver = LocalContentResolver::new(dir.path()).unwrap();

        let content = resolver.resolve("file").await.unwrap();
        assert!(content.contains("# File"));
    }

    #[tokio::test]
    async fn test_resolve_subdir_readme() {
        let dir = setup_test_dir();
        let resolver = LocalContentResolver::new(dir.path()).unwrap();

        let content = resolver.resolve("subdir").await.unwrap();
        assert!(content.contains("# Subdir README"));
    }

    #[tokio::test]
    async fn test_resolve_not_found() {
        let dir = setup_test_dir();
        let resolver = LocalContentResolver::new(dir.path()).unwrap();

        let result = resolver.resolve("nonexistent").await;
        assert!(matches!(result, Err(Error::NotFound(_))));
    }

    #[tokio::test]
    async fn test_resolve_path_traversal() {
        let dir = setup_test_dir();
        let resolver = LocalContentResolver::new(dir.path()).unwrap();

        let result = resolver.resolve("../../../etc/passwd").await;
        assert!(matches!(result, Err(Error::PathTraversal { .. })));
    }
}
