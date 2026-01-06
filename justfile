release-cli version:
    #!/usr/bin/env bash
    set -euo pipefail

    [[ "{{version}}" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]] || \
        { echo "error: invalid version (use semver, e.g. 0.1.0)"; exit 1; }

    git diff --quiet HEAD || { echo "error: uncommitted changes"; exit 1; }

    echo "Release cli-v{{version}}:"
    echo "  - Update core/Cargo.toml"
    echo "  - Commit, tag, push"
    read -p "Continue? [y/N] " c && [[ "$c" =~ ^[Yy]$ ]] || exit 0

    if [[ "$OSTYPE" == darwin* ]]; then
        sed -i '' 's/^version = ".*"/version = "{{version}}"/' core/Cargo.toml
    else
        sed -i 's/^version = ".*"/version = "{{version}}"/' core/Cargo.toml
    fi

    git add core/Cargo.toml
    git commit -m "chore(cli): release v{{version}}"
    git tag "cli-v{{version}}"
    git push origin HEAD "cli-v{{version}}"

    echo "https://github.com/statespace-ai/toolfront/actions"
