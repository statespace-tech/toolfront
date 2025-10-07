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

if ! git diff-index --quiet HEAD -- ':!pyproject.toml'; then
    log_error "You have uncommitted changes (other than pyproject.toml). Please commit or stash them first."
    exit 1
fi

CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
log_info "Current version in pyproject.toml: $CURRENT_VERSION"

# Check git for the last released version
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
LAST_VERSION=${LAST_TAG#v}

if [ "$CURRENT_VERSION" == "$LAST_VERSION" ]; then
    log_error "Version not bumped! Current version ($CURRENT_VERSION) matches last tag ($LAST_TAG)"
    log_error "Please update the version in pyproject.toml first, then run this script"
    echo
    echo "Suggested next versions:"
    IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
    MAJOR=${VERSION_PARTS[0]}
    MINOR=${VERSION_PARTS[1]}
    PATCH=${VERSION_PARTS[2]}
    echo "  Patch: $MAJOR.$MINOR.$((PATCH + 1))"
    echo "  Minor: $MAJOR.$((MINOR + 1)).0"
    echo "  Major: $((MAJOR + 1)).0.0"
    exit 1
fi

NEW_VERSION="$CURRENT_VERSION"
log_info "Preparing to release version: $NEW_VERSION"

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

# Check if this version has already been released
PYPI_EXISTS=false
GIT_TAG_EXISTS=false
NEED_COMMIT=false

# Check if there are uncommitted changes to pyproject.toml
if git diff --name-only | grep -q "pyproject.toml"; then
    NEED_COMMIT=true
    log_info "Detected uncommitted changes to pyproject.toml"
fi

if check_pypi_version "$NEW_VERSION"; then
    PYPI_EXISTS=true
    log_warning "Version $NEW_VERSION already exists on PyPI"
fi

if check_git_tag "$NEW_VERSION"; then
    GIT_TAG_EXISTS=true
    log_warning "Git tag v$NEW_VERSION already exists"
fi

# Determine what steps need to be performed
NEED_PYPI_PUBLISH=false
NEED_GIT_TAG=false

if [ "$PYPI_EXISTS" = false ]; then
    NEED_PYPI_PUBLISH=true
fi

if [ "$GIT_TAG_EXISTS" = false ]; then
    NEED_GIT_TAG=true
fi

if [ "$NEED_COMMIT" = false ] && [ "$NEED_PYPI_PUBLISH" = false ] && [ "$NEED_GIT_TAG" = false ]; then
    log_success "Version $NEW_VERSION has already been fully released!"
    exit 0
fi

echo
log_info "Release plan for version $NEW_VERSION:"
[ "$NEED_COMMIT" = true ] && echo "  ✓ Commit version bump in pyproject.toml"
[ "$NEED_PYPI_PUBLISH" = true ] && echo "  ✓ Build and publish to PyPI"
[ "$NEED_GIT_TAG" = true ] && echo "  ✓ Create and push git tag"
echo

echo "Continue with release? [y/N]"
read -r response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    log_info "Release cancelled."
    exit 0
fi

if [ "$NEED_COMMIT" = true ]; then
    log_info "Committing version bump to $NEW_VERSION"
    git add pyproject.toml
    git commit --no-verify -m "bump version to $NEW_VERSION"
    log_success "Version bump committed"
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

if [ "$NEED_COMMIT" = true ] || [ "$NEED_GIT_TAG" = true ]; then
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
echo "  🏷️  Tag: https://github.com/statespace-ai/toolfront/releases/tag/v$NEW_VERSION"
