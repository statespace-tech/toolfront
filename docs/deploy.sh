#!/bin/bash
# Deploy script for Fly.io documentation

set -e

echo "Preparing deployment files..."

# Copy necessary files from parent directory
cp ../pyproject.toml .
cp ../uv.lock . 2>/dev/null || true  # uv.lock might not exist
cp -r ../src .
cp ../mkdocs.yml .

# Deploy to Fly
echo "Deploying to Fly.io..."
flyctl deploy

# Clean up copied files
echo "Cleaning up..."
rm -f pyproject.toml uv.lock mkdocs.yml
rm -rf src

echo "Deployment complete!"