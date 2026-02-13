# AGENTS.md - Statespace

## Overview

Statespace is an open-source AI runtime/framework. This monorepo contains the Rust implementation.

## Build/Test Commands

- **Build**: `cargo build`
- **Test**: `cargo test`
- **Lint**: `cargo clippy --all-targets -- -D warnings`
- **Format**: `cargo fmt --all`
- **Check**: `cargo check`

## Pre-commit Hooks

Pre-commit hooks run `cargo fmt --check` and `cargo clippy`. To enable:

```bash
git config core.hooksPath .githooks
```

**Note**: On macOS, the linker needs to find `libiconv` (pulled in by reqwest/rustls). The `.envrc` handles this automatically with `direnv`. Without direnv, set:
```bash
export LIBRARY_PATH="$(xcrun --show-sdk-path)/usr/lib${LIBRARY_PATH:+:$LIBRARY_PATH}"
```

## Project Structure

```
statespace/
├── Cargo.toml                      # Workspace manifest
├── shell.nix                       # Nix development environment
├── binaries/
│   └── statespace-cli/             # CLI binary
│       └── src/
│           ├── main.rs
│           ├── args.rs
│           ├── config.rs
│           ├── error.rs
│           ├── commands/
│           └── gateway/
├── crates/
│   ├── statespace-tool-runtime/    # Core runtime library (no HTTP, no CLI)
│   │   └── src/
│   │       ├── lib.rs
│   │       ├── error.rs
│   │       ├── executor.rs
│   │       ├── frontmatter.rs
│   │       ├── protocol.rs
│   │       ├── security.rs
│   │       ├── spec.rs
│   │       ├── tools.rs
│   │       └── validation.rs
│   └── statespace-server/          # HTTP server library
│       └── src/
│           ├── lib.rs
│           ├── content.rs
│           ├── error.rs
│           ├── init.rs
│           ├── server.rs
│           └── templates.rs
└── docs/
    └── design/                     # RFDs
```

## Architecture

Follows FP-Rust patterns aligned with gateway principles:
- **Pure modules** (no I/O): `frontmatter`, `spec`, `security`, `protocol`, `validation`, `templates`
- **Effectful edge**: `executor`, `content`, `server`, `init`
- **Type-driven design**: prefer validated enums/newtypes to make invalid states unrepresentable
- **Explicit dependencies**: pass config and clients explicitly; avoid hidden global state
- **Effects at the edges**: isolate I/O and side effects from domain logic


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

## Design Documents

See [docs/design/](docs/design/) for design documents following the Oxide RFD style.
