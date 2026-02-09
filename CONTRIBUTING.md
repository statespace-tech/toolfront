# Contributing to Statespace

Contributions are welcome. This document covers the basics.

## Getting Started

1. Fork and clone the repository:
   ```
   git clone https://github.com/<your-username>/statespace.git
   cd statespace
   ```
2. Build the project:
   ```
   cargo build
   ```
   The CLI binary is located in `binaries/statespace-cli`.

## Development

Before submitting changes, ensure your code passes all checks:

```
cargo fmt --all -- --check
cargo clippy --workspace -- -D warnings
cargo test --workspace
```

The project uses strict Clippy lints. Calls to `unwrap()`, `expect()`, and `panic!()` are denied. Handle errors explicitly using `Result` or `Option` combinators.

## Submitting Changes

1. Create a branch from `main`.
2. Make your changes in small, focused commits.
3. Ensure all checks listed above pass.
4. Open a pull request against `main` with a clear description of the change.
5. Address review feedback.

## Code Style

- Run `cargo fmt` before committing.
- Follow existing conventions in the codebase.
- No `unwrap()`, `expect()`, or `panic!()`.
- Write tests for new functionality.

## License

Contributions are accepted under the [MIT License](LICENSE).
