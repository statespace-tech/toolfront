use rand::Rng;

const ADJECTIVES: &[&str] = &[
    "alpine", "amber", "ancient", "autumn", "bold", "bright", "calm", "cedar", "clear", "clever",
    "cold", "copper", "coral", "cosmic", "crimson", "crystal", "dark", "dawn", "deep", "dusty",
    "eager", "emerald", "fading", "fierce", "floral", "foggy", "forest", "frozen", "gentle",
    "gilded", "glacial", "golden", "grand", "green", "hollow", "hushed", "icy", "ivory", "jade",
    "keen", "lemon", "light", "linen", "little", "lone", "lucky", "lunar", "maple", "marble",
    "misty", "mossy", "noble", "oak", "ocean", "olive", "opal", "pale", "peach", "pine", "plain",
    "polar", "proud", "quiet", "rapid", "rainy", "rocky", "rosy", "royal", "ruby", "rusty", "sage",
    "sandy", "scarlet", "shadow", "sharp", "silent", "silver", "sleek", "smoky", "snowy", "solar",
    "spicy", "starry", "steel", "still", "stone", "stormy", "sunny", "swift", "tawny", "teal",
    "tender", "timber", "tiny", "velvet", "violet", "vivid", "warm", "wild", "windy", "young",
];

const NOUNS: &[&str] = &[
    "bay", "birch", "bird", "bloom", "bluff", "bolt", "brook", "bush", "cape", "cave", "cliff",
    "cloud", "coast", "cove", "crane", "creek", "crow", "dale", "dawn", "deer", "dove", "drift",
    "dune", "dust", "elm", "ember", "fern", "field", "finch", "flame", "flint", "fog", "ford",
    "fox", "frost", "gale", "gate", "glen", "grove", "gust", "hawk", "haze", "heath", "hill",
    "holly", "isle", "ivy", "lake", "lark", "leaf", "ledge", "lily", "marsh", "mist", "moon",
    "moss", "nest", "oak", "owl", "path", "peak", "pear", "pine", "plum", "pond", "rain", "reed",
    "reef", "ridge", "river", "rock", "rose", "sage", "sand", "shade", "shell", "shore", "sky",
    "snow", "spark", "spring", "star", "stem", "stone", "storm", "sun", "surf", "thorn", "tide",
    "trail", "tree", "vale", "vine", "wave", "weed", "well", "willow", "wind", "wood", "wren",
];

/// Generate a random environment name in the format `adjective-noun-NNNN`.
///
/// Produces DNS-safe names like `alpine-brook-4821` or `golden-hawk-1337`.
/// The 4-digit suffix reduces collision likelihood across ~10k combinations
/// per adjective-noun pair (~100M total combinations).
pub(crate) fn generate_name() -> String {
    let mut rng = rand::rng();
    let adj = ADJECTIVES[rng.random_range(..ADJECTIVES.len())];
    let noun = NOUNS[rng.random_range(..NOUNS.len())];
    let num: u16 = rng.random_range(1000..10000);
    format!("{adj}-{noun}-{num}")
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
        // Theoretically could collide but with ~100M combinations, vanishingly unlikely
        assert_ne!(a, b);
    }
}
