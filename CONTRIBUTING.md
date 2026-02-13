# Contributing to Statespace

Thanks for your interest in contributing. This repo is 100% open-source Rust. This guide covers how to build, test, and submit changes in a way that keeps the codebase tight and reliable.

## Requirements

- Rust **1.85+** (MSRV) with `rustfmt` and `clippy` components
- Optional: `direnv` (for macOS linker env), `just` (release helper)

To install MSRV explicitly:

```bash
rustup toolchain install 1.85.0
rustup override set 1.85.0
```

## Getting started

1. Fork and clone:
   ```bash
   git clone https://github.com/<your-username>/statespace.git
   cd statespace
   ```
2. Build:
   ```bash
   cargo build
   ```
   The CLI binary lives in `binaries/statespace-cli`.

## Development workflow

Run these before opening a PR:

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
```

Pre-commit hooks (format + clippy):

```bash
git config core.hooksPath .githooks
```

## Code standards

- No `unwrap()`, `expect()`, or `panic!()` in library code (tests are fine).
- Prefer explicit error handling with `Result` and typed enums.
- Keep public APIs documented and test new behavior.
- Follow existing module boundaries and naming conventions.

## Changelog

If your change is user-facing, add a short entry under `## Unreleased` in `CHANGELOG.md`.

## Submitting changes

1. Create a branch from `main`.
2. Keep commits focused and scoped.
3. Open a PR with a clear description, motivation, and test notes.

## License

Contributions are accepted under the [MIT License](LICENSE).
