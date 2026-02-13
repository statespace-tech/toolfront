const SLUG_MIN_LENGTH: usize = 3;
const SLUG_MAX_LENGTH: usize = 63;

const RESERVED_SLUGS: &[&str] = &[
    "api",
    "www",
    "admin",
    "app",
    "dashboard",
    "console",
    "status",
    "docs",
    "help",
    "support",
    "billing",
    "auth",
    "login",
    "signup",
    "static",
    "assets",
    "cdn",
    "mail",
    "smtp",
    "ftp",
    "ssh",
    "git",
];

const ALLOWED_ENV_HOST_SUFFIXES: &[&str] = &["app.statespace.com", "app.staging.statespace.com"];

#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum EnvironmentReference {
    Uuid(String),
    Slug(String),
    Name(String),
}

impl EnvironmentReference {
    pub(crate) fn value(&self) -> &str {
        match self {
            EnvironmentReference::Uuid(value)
            | EnvironmentReference::Slug(value)
            | EnvironmentReference::Name(value) => value,
        }
    }
}

pub(crate) fn slugify_name(name: &str) -> Option<String> {
    let mut slug = String::new();
    let mut last_hyphen = false;

    for ch in name.chars() {
        if ch.is_ascii_alphanumeric() {
            slug.push(ch.to_ascii_lowercase());
            last_hyphen = false;
        } else if !last_hyphen {
            slug.push('-');
            last_hyphen = true;
        }
    }

    let slug = slug.trim_matches('-');
    if slug.is_empty() {
        return None;
    }

    let mut slug = slug.to_string();
    if slug.len() > SLUG_MAX_LENGTH {
        slug.truncate(SLUG_MAX_LENGTH);
        while slug.ends_with('-') {
            slug.pop();
        }
    }

    if slug.len() < SLUG_MIN_LENGTH {
        return None;
    }

    if !is_valid_slug(&slug) {
        return None;
    }

    Some(slug)
}

pub(crate) fn normalize_environment_reference(input: &str) -> Result<EnvironmentReference, String> {
    if input.contains("://") {
        if let Some(slug) = parse_slug_from_url(input) {
            return Ok(EnvironmentReference::Slug(slug));
        }
        return Err(format!(
            "Invalid environment URL: {input}. Expected https://{{slug}}.app.statespace.com"
        ));
    }

    if is_uuid_like(input) {
        return Ok(EnvironmentReference::Uuid(input.to_string()));
    }

    if is_valid_slug(input) {
        return Ok(EnvironmentReference::Slug(input.to_string()));
    }

    Ok(EnvironmentReference::Name(input.to_string()))
}

fn parse_slug_from_url(input: &str) -> Option<String> {
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
            let slug = stripped.strip_suffix('.').unwrap_or(stripped);
            if is_valid_slug(slug) {
                return Some(slug.to_string());
            }
        }
    }
    None
}

fn is_valid_slug(value: &str) -> bool {
    let len = value.len();
    if !(SLUG_MIN_LENGTH..=SLUG_MAX_LENGTH).contains(&len) {
        return false;
    }
    if value.starts_with('-') || value.ends_with('-') || value.contains("--") {
        return false;
    }
    if RESERVED_SLUGS.iter().any(|reserved| reserved == &value) {
        return false;
    }

    value
        .chars()
        .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-')
}

fn is_uuid_like(value: &str) -> bool {
    if value.len() != 36 {
        return false;
    }

    for (idx, ch) in value.chars().enumerate() {
        let is_hyphen_position = matches!(idx, 8 | 13 | 18 | 23);
        if is_hyphen_position {
            if ch != '-' {
                return false;
            }
            continue;
        }
        if !ch.is_ascii_hexdigit() {
            return false;
        }
    }
    true
}

#[cfg(test)]
#[allow(clippy::expect_used)]
mod tests {
    use super::{
        EnvironmentReference, normalize_environment_reference, parse_slug_from_url, slugify_name,
    };

    #[test]
    fn slugify_basic() {
        assert_eq!(slugify_name("My App"), Some("my-app".to_string()));
        assert_eq!(
            slugify_name("  Spaces   Everywhere "),
            Some("spaces-everywhere".to_string())
        );
    }

    #[test]
    fn slugify_rejects_short_or_reserved() {
        assert_eq!(slugify_name("api"), None);
        assert_eq!(slugify_name("a"), None);
    }

    #[test]
    fn parse_slug_from_url_accepts_env_domains() {
        assert_eq!(
            parse_slug_from_url("https://blue-mountain-1234.app.statespace.com"),
            Some("blue-mountain-1234".to_string())
        );
        assert_eq!(
            parse_slug_from_url("https://blue-mountain-1234.app.staging.statespace.com"),
            Some("blue-mountain-1234".to_string())
        );
    }

    #[test]
    fn normalize_reference_uuid() {
        let ref_value = normalize_environment_reference("550e8400-e29b-41d4-a716-446655440000")
            .expect("expected uuid");
        assert!(matches!(ref_value, EnvironmentReference::Uuid(_)));
    }

    #[test]
    fn normalize_reference_slug() {
        let ref_value =
            normalize_environment_reference("blue-mountain-1234").expect("expected slug");
        assert_eq!(
            ref_value,
            EnvironmentReference::Slug("blue-mountain-1234".to_string())
        );
    }

    #[test]
    fn normalize_reference_url() {
        let ref_value =
            normalize_environment_reference("https://blue-mountain-1234.app.statespace.com")
                .expect("expected slug from url");
        assert_eq!(
            ref_value,
            EnvironmentReference::Slug("blue-mountain-1234".to_string())
        );
    }
}
