#!/bin/bash
# dev-clean.sh: Remove temporary and cache files from the project.
# Run this from any location; it searches from the project root.

set -e

echo "Starting cleanup of temporary files..."

# Remove all __pycache__ directories from the project root
echo "Removing __pycache__ directories..."
find .. -type d -name '__pycache__' -exec rm -rf {} +

# Remove all .pyc files from the project root
echo "Removing .pyc files..."
find .. -type f -name '*.pyc' -delete

# Remove all .pyo files from the project root
echo "Removing .pyo files..."
find .. -type f -name '*.pyo' -delete

# Remove the .pytest_cache directories from the project root
echo "Removing .pytest_cache directories..."
find .. -type d -name '.pytest_cache' -exec rm -rf {} +

# Remove backup files ending with a tilde (~)
echo "Removing backup files..."
find .. -type f -name '*~' -delete

echo "Cleanup complete!"
