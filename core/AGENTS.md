# AGENTS.md - Statespace Core (Rust)

## Overview

This is the Rust implementation of the Statespace server - an open-source AI tool execution runtime.

## Build/Test Commands

- **Build**: `cargo build`
- **Test**: `cargo test`
- **Lint**: `cargo clippy`
- **Format**: `cargo fmt`
- **Check**: `cargo check`

**Note**: On macOS, run inside `nix-shell` to get `libiconv` linked properly:
```bash
nix-shell --run "cargo build"
nix-shell --run "cargo test"
```

## Project Structure

```
core/
├── Cargo.toml                      # Workspace manifest with lints
├── shell.nix                       # Nix development environment
└── crates/
    ├── statespace-tool-runtime/    # Pure domain logic (no HTTP, no CLI)
    │   └── src/
    │       ├── lib.rs
    │       ├── error.rs
    │       ├── executor.rs
    │       ├── frontmatter.rs
    │       ├── protocol.rs
    │       ├── security.rs
    │       ├── spec.rs
    │       ├── tools.rs
    │       └── validation.rs
    │
    ├── statespace-server/          # HTTP server library (no CLI)
    │   └── src/
    │       ├── lib.rs
    │       ├── content.rs
    │       ├── error.rs
    │       ├── init.rs
    │       ├── server.rs
    │       └── templates.rs
    │
    └── statespace-cli/             # CLI binary
        └── src/
            ├── main.rs
            ├── args.rs
            ├── config.rs
            ├── error.rs
            ├── commands/
            │   ├── mod.rs
            │   ├── app.rs
            │   └── tokens.rs
            └── gateway/
                ├── mod.rs
                ├── client.rs
                └── types.rs
```

## Architecture

Follows FP-Rust patterns:
- **Pure modules** (no I/O): `frontmatter`, `spec`, `security`, `protocol`, `validation`, `templates`
- **Effectful edge**: `executor`, `content`, `server`, `init`

### Dependency Graph

```
statespace-cli ──► statespace-server ──► statespace-tool-runtime
       │                                          ▲
       └──────────────────────────────────────────┘
```

## Rust Code Guidelines

- Do NOT use `unwrap()` or `expect()` or anything that panics in library code - handle errors properly. In tests, `unwrap()` and `panic!()` are fine.

- Prefer `crate::` over `super::` for imports. Clean it up if you see `super::`.

- Avoid using `pub use` on imports unless you are re-exposing a dependency so downstream consumers do not have to depend on it directly.

- Skip global state via `lazy_static!`, `Once`, or similar; prefer passing explicit context structs for any shared state.

## CLI Commands

```bash
# Serve a tool site locally
nix-shell --run "cargo run -p statespace-cli -- app serve /path/to/toolsite"

# Deploy to cloud
nix-shell --run "cargo run -p statespace-cli -- app deploy /path/to/toolsite --name myapp"

# List apps
nix-shell --run "cargo run -p statespace-cli -- app list"

# Token management
nix-shell --run "cargo run -p statespace-cli -- tokens list"
```

## Design Document

See [docs/design/001-statespace-server.md](../docs/design/001-statespace-server.md) for the full design.
