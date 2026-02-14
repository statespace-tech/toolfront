/// Generate a random environment name in the format `adjective-noun-NNNN`.
///
/// Uses the `petname` crate's curated word lists (Dustin Kirkland's petname
/// project, widely adopted across Docker/Ubuntu/Heroku-style tooling).
/// The 4-digit suffix reduces collision likelihood (~90M+ total combinations).
pub(crate) fn generate_name() -> String {
    let base = petname::petname(2, "-").unwrap_or_else(|| "env".to_string());
    let num = random_suffix();
    format!("{base}-{num}")
}

/// 4-digit random suffix (1000–9999) using std randomness.
fn random_suffix() -> u16 {
    use std::collections::hash_map::RandomState;
    use std::hash::{BuildHasher, Hasher};
    let hash = RandomState::new().build_hasher().finish();
    (hash % 9000) as u16 + 1000
}

#[cfg(test)]
mod tests {
    use crate::names::generate_name;

    #[test]
    fn generated_name_is_dns_safe() {
        for _ in 0..100 {
            let name = generate_name();
            assert!(name.len() >= 3);
            assert!(name.len() <= 63);
            assert!(!name.starts_with('-'));
            assert!(!name.ends_with('-'));
            assert!(!name.contains("--"));
            assert!(
                name.chars()
                    .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || c == '-')
            );
        }
    }

    #[test]
    fn generated_names_are_not_identical() {
        let a = generate_name();
        let b = generate_name();
        assert_ne!(a, b);
    }
}
