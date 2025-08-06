#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    log_error "Must be on main branch to release. Current branch: $CURRENT_BRANCH"
    exit 1
fi

if ! git diff-index --quiet HEAD --; then
    log_error "You have uncommitted changes. Please commit or stash them first."
    exit 1
fi

CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
log_info "Current version: $CURRENT_VERSION"

check_pypi_version() {
    local version="$1"
    log_info "Checking if version $version exists on PyPI..."
    if curl -s "https://pypi.org/pypi/toolfront/$version/json" | grep -q "Not Found"; then
        return 1  # Version does not exist
    else
        return 0  # Version exists
    fi
}

check_git_tag() {
    local version="$1"
    if git tag -l | grep -q "^v$version$"; then
        return 0  # Tag exists
    else
        return 1  # Tag does not exist
    fi
}

if [ -n "$1" ]; then
    NEW_VERSION="$1"
    log_info "Using provided version: $NEW_VERSION"
    
    if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format. Please use X.Y.Z format (e.g., 0.2.0)"
        exit 1
    fi
else
    # Auto-increment patch version
    IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
    MAJOR=${VERSION_PARTS[0]}
    MINOR=${VERSION_PARTS[1]}
    PATCH=${VERSION_PARTS[2]}
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
    
    log_info "Auto-bumping patch version to: $NEW_VERSION"
fi

# Check if this version has already been released
PYPI_EXISTS=false
GIT_TAG_EXISTS=false
VERSION_BUMP_NEEDED=true

if check_pypi_version "$NEW_VERSION"; then
    PYPI_EXISTS=true
    log_warning "Version $NEW_VERSION already exists on PyPI"
fi

if check_git_tag "$NEW_VERSION"; then
    GIT_TAG_EXISTS=true
    log_warning "Git tag v$NEW_VERSION already exists"
fi

if [ "$CURRENT_VERSION" == "$NEW_VERSION" ]; then
    VERSION_BUMP_NEEDED=false
    log_info "Version is already set to $NEW_VERSION in pyproject.toml"
fi

# Determine what steps need to be performed
NEED_VERSION_BUMP=false
NEED_PYPI_PUBLISH=false
NEED_GIT_PUSH=false
NEED_GIT_TAG=false

if [ "$VERSION_BUMP_NEEDED" = true ]; then
    NEED_VERSION_BUMP=true
    NEED_GIT_PUSH=true
fi

if [ "$PYPI_EXISTS" = false ]; then
    NEED_PYPI_PUBLISH=true
fi

if [ "$GIT_TAG_EXISTS" = false ]; then
    NEED_GIT_TAG=true
fi

if [ "$NEED_VERSION_BUMP" = false ] && [ "$NEED_PYPI_PUBLISH" = false ] && [ "$NEED_GIT_TAG" = false ]; then
    log_success "Version $NEW_VERSION has already been fully released!"
    exit 0
fi

echo
log_info "Release plan for version $NEW_VERSION:"
[ "$NEED_VERSION_BUMP" = true ] && echo "  ✓ Bump version in pyproject.toml and commit"
[ "$NEED_PYPI_PUBLISH" = true ] && echo "  ✓ Build and publish to PyPI"
[ "$NEED_GIT_PUSH" = true ] && echo "  ✓ Push commits to remote"
[ "$NEED_GIT_TAG" = true ] && echo "  ✓ Create and push git tag"
echo

echo "Continue with release? [y/N]"
read -r response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    log_info "Release cancelled."
    exit 0
fi

if [ "$NEED_VERSION_BUMP" = true ]; then
    log_info "Bumping version from $CURRENT_VERSION to $NEW_VERSION"
    sed -i "" "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    git add pyproject.toml
    git commit --no-verify -m "bump version to $NEW_VERSION"
    log_success "Version bumped and committed"
fi

if [ "$NEED_PYPI_PUBLISH" = true ]; then
    log_info "Building package..."
    rm -rf dist/*
    uv build
    
    log_info "Publishing to PyPI..."
    if [ -z "$PYPI_API_TOKEN" ]; then
        log_error "PYPI_API_TOKEN environment variable not set"
        exit 1
    fi
    
    if uv publish --token "$PYPI_API_TOKEN"; then
        log_success "Published to PyPI"
    else
        log_error "Failed to publish to PyPI"
        exit 1
    fi
fi

if [ "$NEED_GIT_PUSH" = true ]; then
    log_info "Pushing commits to remote..."
    if git push; then
        log_success "Commits pushed to remote"
    else
        log_error "Failed to push commits"
        exit 1
    fi
fi

if [ "$NEED_GIT_TAG" = true ]; then
    log_info "Creating git tag v$NEW_VERSION..."
    git tag "v$NEW_VERSION"
    
    log_info "Pushing tag to remote..."
    if git push origin "v$NEW_VERSION"; then
        log_success "Tag v$NEW_VERSION pushed to remote"
    else
        log_error "Failed to push tag"
        exit 1
    fi
fi

echo
log_success "Successfully released version $NEW_VERSION!"
echo
log_info "Summary:"
echo "  📦 PyPI: https://pypi.org/project/toolfront/$NEW_VERSION/"
echo "  🏷️  Tag: https://github.com/kruskal-labs/toolfront/releases/tag/v$NEW_VERSION"
