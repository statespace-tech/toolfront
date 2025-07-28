#!/bin/bash
set -e

VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Building Docker image for version: $VERSION"

echo "Building Docker image..."
docker build -t antidmg/toolfront:$VERSION .
docker build -t antidmg/toolfront:latest .

echo "Pushing Docker image..."
docker push antidmg/toolfront:$VERSION
docker push antidmg/toolfront:latest

echo "Successfully built and pushed Docker images for version $VERSION"
