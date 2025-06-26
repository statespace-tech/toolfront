#!/bin/bash
set -e

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Error: You have uncommitted changes. Please commit or stash them first."
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $CURRENT_VERSION"

# Increment patch version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"

echo "Bumping version to: $NEW_VERSION"

# Update version in pyproject.toml
sed -i "" "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Commit version bump
git add pyproject.toml
git commit -m "bump version to $NEW_VERSION"

# Clean dist directory
rm -rf dist/*

# Build
echo "Building package..."
uv build

# Publish
echo "Publishing to PyPI..."
if [ -z "$PYPI_API_TOKEN" ]; then
    echo "Error: PYPI_API_TOKEN environment variable not set"
    exit 1
fi

uv publish --token "$PYPI_API_TOKEN"

# Push commit
git push

# Create and push tag
git tag "v$NEW_VERSION"
git push origin "v$NEW_VERSION"

echo "Successfully released version $NEW_VERSION"
