#!/bin/bash
# Deploy script for Fly.io documentation

set -e

echo "Preparing deployment files..."

# Copy zensical.toml from parent directory
cp ../zensical.toml .

# Deploy to Fly
echo "Deploying to Fly.io..."
flyctl deploy

# Clean up copied files
echo "Cleaning up..."
rm -f zensical.toml

echo "Deployment complete!"