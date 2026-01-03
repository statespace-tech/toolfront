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
├── Cargo.toml              # Workspace manifest
├── shell.nix               # Nix development environment
└── crates/
    └── statespace-server/  # Main library + binary crate
        ├── src/
        │   ├── lib.rs      # Library entry point
        │   ├── main.rs     # CLI binary
        │   ├── content.rs  # File resolution (ContentResolver trait)
        │   ├── error.rs    # Error types
        │   ├── executor.rs # Tool execution (ToolExecutor)
        │   ├── frontmatter.rs # YAML/TOML parsing
        │   ├── init.rs     # Template initialization (effectful)
        │   ├── protocol.rs # Request/response types
        │   ├── security.rs # SSRF protection
        │   ├── server.rs   # Axum router
        │   ├── spec.rs     # Tool specification validation
        │   ├── templates.rs # Embedded templates (pure)
        │   ├── tools.rs    # BuiltinTool enum
        │   └── validation.rs # Command validation
        └── README.md
```

## Architecture

Follows FP-Rust patterns:
- **Pure modules** (no I/O): `frontmatter`, `spec`, `security`, `protocol`, `validation`, `templates`
- **Effectful edge**: `executor`, `content`, `server`, `init`

## Running the Server

```bash
nix-shell --run "cargo run -- /path/to/toolsite --port 8000"

# Skip template initialization
nix-shell --run "cargo run -- /path/to/toolsite --port 8000 --no-init"
```

## Design Document

See [docs/design/001-statespace-server.md](../docs/design/001-statespace-server.md) for the full design.
