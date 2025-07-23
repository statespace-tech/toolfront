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

# Check if version was provided as argument
if [ -n "$1" ]; then
    NEW_VERSION="$1"
    echo "Using provided version: $NEW_VERSION"
    
    # Validate version format
    if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Invalid version format. Please use X.Y.Z format (e.g., 0.2.0)"
        exit 1
    fi
    
    # Check if version is already set
    if [ "$CURRENT_VERSION" == "$NEW_VERSION" ]; then
        echo "Version is already set to $NEW_VERSION, skipping version bump commit"
    else
        # Update version in pyproject.toml
        sed -i "" "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
        
        # Commit version bump
        git add pyproject.toml
        git commit -m "bump version to $NEW_VERSION"
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
    
    # Update version in pyproject.toml
    sed -i "" "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    
    # Commit version bump
    git add pyproject.toml
    git commit -m "bump version to $NEW_VERSION"
fi

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

# Build and push Docker image
echo "Building Docker image..."
docker build -t antidmg/toolfront:$NEW_VERSION .
docker build -t antidmg/toolfront:latest .

echo "Pushing Docker image..."
docker push antidmg/toolfront:$NEW_VERSION
docker push antidmg/toolfront:latest

# Push commit
git push

# Create and push tag
git tag "v$NEW_VERSION"
git push origin "v$NEW_VERSION"

echo "Successfully released version $NEW_VERSION"
