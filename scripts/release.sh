#!/bin/bash
set -e

if ! git diff-index --quiet HEAD --; then
    echo "Error: You have uncommitted changes. Please commit or stash them first."
    exit 1
fi

CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $CURRENT_VERSION"

if [ -n "$1" ]; then
    NEW_VERSION="$1"
    echo "Using provided version: $NEW_VERSION"
    
    if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Invalid version format. Please use X.Y.Z format (e.g., 0.2.0)"
        exit 1
    fi
    
    if [ "$CURRENT_VERSION" == "$NEW_VERSION" ]; then
        echo "Version is already set to $NEW_VERSION, skipping version bump commit"
    else
        sed -i "" "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
        
        git add pyproject.toml

        # don't run the linter
        echo "About to commit version bump. Continue? [y/N]"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            git commit --no-verify -m "bump version to $NEW_VERSION"
        else
            echo "Commit cancelled. Exiting."
            git reset HEAD pyproject.toml
            exit 1
        fi
    fi
else
    # Auto-increment patch version
    IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
    MAJOR=${VERSION_PARTS[0]}
    MINOR=${VERSION_PARTS[1]}
    PATCH=${VERSION_PARTS[2]}
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
    
    echo "Auto-bumping patch version to: $NEW_VERSION"
    
    sed -i "" "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    
    # Commit version bump
    git add pyproject.toml
    echo "About to commit version bump. Continue? [y/N]"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        git commit --no-verify -m "bump version to $NEW_VERSION"
    else
        echo "Commit cancelled. Exiting."
        git reset HEAD pyproject.toml
        exit 1
    fi
fi

rm -rf dist/*

echo "Building package..."
uv build

echo "Publishing to PyPI..."
if [ -z "$PYPI_API_TOKEN" ]; then
    echo "Error: PYPI_API_TOKEN environment variable not set"
    exit 1
fi

uv publish --token "$PYPI_API_TOKEN"

echo "About to push commits to remote. Continue? [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    git push
else
    echo "Push cancelled. Exiting."
    exit 1
fi

git tag "v$NEW_VERSION"
echo "About to push tag v$NEW_VERSION to remote. Continue? [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    git push origin "v$NEW_VERSION"
else
    echo "Tag push cancelled. Tag created locally but not pushed."
    exit 1
fi

echo "Successfully released version $NEW_VERSION"
