const ALLOWED_ENV_HOST_SUFFIXES: &[&str] = &["app.statespace.com", "app.staging.statespace.com"];

/// Normalize user input into a value the gateway can resolve.
///
/// The gateway accepts UUIDs, short IDs, and names (slug-format) in path parameters.
/// The CLI's only job is to extract a name from a URL if one is pasted — everything
/// else is passed through verbatim and resolved server-side.
pub(crate) fn normalize_environment_reference(input: &str) -> Result<String, String> {
    if input.contains("://") {
        if let Some(name) = parse_name_from_url(input) {
            return Ok(name);
        }
        return Err(format!(
            "Invalid environment URL: {input}. Expected https://{{name}}.app.statespace.com"
        ));
    }

    Ok(input.to_string())
}

fn parse_name_from_url(input: &str) -> Option<String> {
    let url = reqwest::Url::parse(input).ok()?;
    let scheme = url.scheme();
    if scheme != "http" && scheme != "https" {
        return None;
    }

    let host = url.host_str()?;
    for suffix in ALLOWED_ENV_HOST_SUFFIXES {
        if host == *suffix {
            return None;
        }
        if let Some(stripped) = host.strip_suffix(suffix) {
            let name = stripped.strip_suffix('.').unwrap_or(stripped);
            if !name.is_empty() {
                return Some(name.to_string());
            }
        }
    }
    None
}

#[cfg(test)]
#[allow(clippy::expect_used)]
mod tests {
    use crate::identifiers::{normalize_environment_reference, parse_name_from_url};

    #[test]
    fn parse_name_from_url_accepts_env_domains() {
        assert_eq!(
            parse_name_from_url("https://my-cool-project.app.statespace.com"),
            Some("my-cool-project".to_string())
        );
        assert_eq!(
            parse_name_from_url("https://my-cool-project.app.staging.statespace.com"),
            Some("my-cool-project".to_string())
        );
    }

    #[test]
    fn parse_name_from_url_rejects_bare_domain() {
        assert_eq!(parse_name_from_url("https://app.statespace.com"), None);
        assert_eq!(
            parse_name_from_url("https://app.staging.statespace.com"),
            None
        );
    }

    #[test]
    fn normalize_uuid_passthrough() {
        let result = normalize_environment_reference("550e8400-e29b-41d4-a716-446655440000")
            .expect("should pass through");
        assert_eq!(result, "550e8400-e29b-41d4-a716-446655440000");
    }

    #[test]
    fn normalize_name_passthrough() {
        let result =
            normalize_environment_reference("my-cool-project").expect("should pass through");
        assert_eq!(result, "my-cool-project");
    }

    #[test]
    fn normalize_url_extracts_name() {
        let result = normalize_environment_reference("https://my-cool-project.app.statespace.com")
            .expect("should extract name from url");
        assert_eq!(result, "my-cool-project");
    }

    #[test]
    fn normalize_rejects_invalid_url() {
        let result = normalize_environment_reference("https://example.com/something");
        assert!(result.is_err());
    }
}
