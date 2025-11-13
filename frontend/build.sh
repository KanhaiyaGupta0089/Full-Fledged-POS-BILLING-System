#!/bin/bash
# Build script for frontend deployment

set -e

echo "Installing Node.js dependencies..."
npm install

echo "Building React application..."
npm run build

echo "Frontend build complete!"

