#!/usr/bin/env bash
# build.sh - Custom build script for Render deployment

# Exit on error
set -e

# Upgrade pip
pip install --upgrade pip

# Install dependencies with --only-binary to avoid building wheels
pip install --only-binary=:all: -r requirements.txt

echo "Build completed successfully!"