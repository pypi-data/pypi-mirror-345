#!/bin/bash
# Script to build and publish the package to PyPI

# Set the correct directory
cd /Users/saish/Downloads/tbh_secure_agents/build_dir

# Ensure we have the latest build tools
echo "Upgrading build tools..."
pip install --upgrade pip build twine

# Clean up any previous builds
echo "Cleaning up previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "Building the package..."
python -m build .

# Check the built package
echo "Checking the built package..."
twine check dist/*

# Ask for confirmation before publishing
echo ""
echo "Package is ready to be published to PyPI."
echo "Version: $(grep "version" pyproject.toml | cut -d'"' -f2)"
echo ""
read -p "Do you want to publish this package to PyPI? (y/n): " confirm

if [ "$confirm" = "y" ]; then
    echo "Publishing to PyPI..."
    twine upload dist/*
    echo "Package published successfully!"
else
    echo "Publishing cancelled."
fi
