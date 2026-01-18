#!/usr/bin/env bash
#
# Statespace CLI Installer
# https://github.com/statespace-tech/statespace
#
# Usage:
#   curl -fsSL https://statespace.com/install.sh | bash
#   STATESPACE_VERSION=0.1.0 curl -fsSL https://statespace.com/install.sh | bash
#

set -euo pipefail

readonly REPO="statespace-tech/statespace"
readonly BINARY_NAME="statespace"
readonly INSTALL_DIR="${STATESPACE_INSTALL_DIR:-$HOME/.statespace}"
readonly BIN_DIR="$INSTALL_DIR/bin"
readonly GITHUB_API="https://api.github.com/repos/${REPO}/releases"
readonly GITHUB_RELEASES="https://github.com/${REPO}/releases/download"

# --- Output ---

if [[ -t 1 ]]; then
    readonly RED=$'\033[0;31m' GREEN=$'\033[0;32m' BLUE=$'\033[0;34m' BOLD=$'\033[1m' NC=$'\033[0m'
else
    readonly RED='' GREEN='' BLUE='' BOLD='' NC=''
fi

info() { printf '%s==>%s %s\n' "$BLUE" "$NC" "$1"; }
error() { printf '%s==>%s %s\n' "$RED" "$NC" "$1" >&2; exit 1; }

# --- Platform Detection ---

detect_target() {
    local os arch

    case "$(uname -s)" in
        Darwin) os="apple-darwin" ;;
        Linux)
            if [[ -f /etc/alpine-release ]] || ldd --version 2>&1 | grep -qi musl; then
                os="unknown-linux-musl"
            else
                os="unknown-linux-gnu"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*|Windows_NT)
            error "Windows is not supported. Use WSL: https://learn.microsoft.com/en-us/windows/wsl/install"
            ;;
        *) error "unsupported operating system: $(uname -s)" ;;
    esac

    case "$(uname -m)" in
        x86_64|amd64) arch="x86_64" ;;
        arm64|aarch64) arch="aarch64" ;;
        *) error "unsupported architecture: $(uname -m)" ;;
    esac

    printf '%s-%s' "$arch" "$os"
}

# --- HTTP ---

check_requirements() {
    if ! command -v curl &>/dev/null && ! command -v wget &>/dev/null; then
        error "curl or wget is required"
    fi
}

fetch() {
    local url="$1"
    if command -v curl &>/dev/null; then
        curl --proto '=https' --tlsv1.2 -fsSL "$url"
    else
        wget --https-only --secure-protocol=TLSv1_2 -qO- "$url"
    fi
}

download() {
    local url="$1" dest="$2"
    if command -v curl &>/dev/null; then
        curl --proto '=https' --tlsv1.2 -fsSL "$url" -o "$dest"
    else
        wget --https-only --secure-protocol=TLSv1_2 -q "$url" -O "$dest"
    fi
}

# --- Version ---

get_latest_version() {
    local response
    response=$(fetch "$GITHUB_API") || error "failed to fetch releases from GitHub API"

    # Find the first cli-v* tag (releases are sorted by date, newest first)
    local version
    version=$(printf '%s' "$response" | grep -o '"tag_name"[[:space:]]*:[[:space:]]*"cli-v[^"]*"' | head -1 | \
        sed 's/.*"cli-v\([^"]*\)".*/\1/')

    [[ -n "$version" ]] || error "no CLI releases found"
    printf '%s' "$version"
}

# --- Checksum ---

compute_sha256() {
    local file="$1"
    if command -v sha256sum &>/dev/null; then
        sha256sum "$file" | cut -d' ' -f1
    elif command -v shasum &>/dev/null; then
        shasum -a 256 "$file" | cut -d' ' -f1
    else
        error "sha256sum or shasum is required for checksum verification"
    fi
}

verify_checksum() {
    local file="$1" expected="$2"
    local actual
    actual=$(compute_sha256 "$file")

    if [[ "$actual" != "$expected" ]]; then
        error "checksum verification failed
  expected: $expected
  actual:   $actual

This could indicate a corrupted download or a security issue.
Please report this at: https://github.com/${REPO}/issues"
    fi
}

# --- PATH ---

setup_path() {
    # Already in PATH
    if command -v "$BINARY_NAME" &>/dev/null; then
        return 0
    fi

    local shell_name rc_file=""
    shell_name=$(basename "${SHELL:-bash}")

    case "$shell_name" in
        bash)
            # Prefer .bashrc for interactive, .bash_profile for login
            if [[ -f "$HOME/.bashrc" ]]; then
                rc_file="$HOME/.bashrc"
            elif [[ -f "$HOME/.bash_profile" ]]; then
                rc_file="$HOME/.bash_profile"
            fi
            ;;
        zsh)
            [[ -f "$HOME/.zshrc" ]] && rc_file="$HOME/.zshrc"
            ;;
        fish)
            [[ -f "$HOME/.config/fish/config.fish" ]] && rc_file="$HOME/.config/fish/config.fish"
            ;;
    esac

    if [[ -n "$rc_file" ]] && ! grep -qF "$BIN_DIR" "$rc_file" 2>/dev/null; then
        if [[ "$shell_name" == "fish" ]]; then
            printf '\nfish_add_path "%s"\n' "$BIN_DIR" >> "$rc_file"
        else
            printf '\nexport PATH="%s:$PATH"\n' "$BIN_DIR" >> "$rc_file"
        fi
        info "added $BIN_DIR to PATH in $rc_file"
    fi
}

# --- Main ---

main() {
    printf '%sStatespace CLI Installer%s\n\n' "$BOLD" "$NC"

    check_requirements

    local target version
    target=$(detect_target)
    info "detected platform: $target"

    if [[ -n "${STATESPACE_VERSION:-}" ]]; then
        version="$STATESPACE_VERSION"
    else
        version=$(get_latest_version)
    fi
    info "installing version: $version"

    # Create secure temp directory (mode 700)
    local tmp_dir
    tmp_dir=$(mktemp -d) || error "failed to create temp directory"
    chmod 700 "$tmp_dir"
    trap 'rm -rf "$tmp_dir"' EXIT

    local archive_name="${BINARY_NAME}-v${version}-${target}.tar.gz"
    local archive_path="$tmp_dir/$archive_name"
    local checksum_path="$tmp_dir/${archive_name}.sha256"
    local base_url="${GITHUB_RELEASES}/cli-v${version}"

    # Download checksum first
    info "fetching checksum..."
    download "$base_url/${archive_name}.sha256" "$checksum_path" || \
        error "failed to download checksum file"
    local expected_checksum
    expected_checksum=$(cut -d' ' -f1 < "$checksum_path")

    # Download archive
    info "downloading $archive_name..."
    download "$base_url/$archive_name" "$archive_path" || \
        error "download failed (version $version may not support $target)"

    # Verify checksum BEFORE extraction
    info "verifying checksum..."
    verify_checksum "$archive_path" "$expected_checksum"

    # Extract to temp directory
    info "extracting..."
    tar -xzf "$archive_path" -C "$tmp_dir" || error "failed to extract archive"

    local extracted_binary="$tmp_dir/${BINARY_NAME}-v${version}-${target}/${BINARY_NAME}"
    [[ -f "$extracted_binary" ]] || error "binary not found in archive"

    # Install
    mkdir -p "$BIN_DIR"
    chmod 755 "$BIN_DIR"

    mv "$extracted_binary" "$BIN_DIR/$BINARY_NAME"
    chmod 755 "$BIN_DIR/$BINARY_NAME"

    info "installed to $BIN_DIR/$BINARY_NAME"

    setup_path

    printf '\n%sInstalled successfully!%s\n' "$GREEN" "$NC"
    printf 'Run: %s --help\n' "$BINARY_NAME"

    if ! command -v "$BINARY_NAME" &>/dev/null; then
        printf '\nTo use now, run:\n  export PATH="%s:$PATH"\n' "$BIN_DIR"
    fi
}

main "$@"
