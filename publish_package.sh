#!/bin/bash

# Snowlate Package Publishing Script
# This script helps publish the Snowlate package to PyPI

set -e

echo "=== Snowlate Package Publishing Script ==="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Extract version from pyproject.toml
PACKAGE_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
PACKAGE_NAME=$(grep '^name = ' pyproject.toml | sed 's/name = "\(.*\)"/\1/')

if [ -z "$PACKAGE_VERSION" ]; then
    echo "Error: Could not extract version from pyproject.toml"
    exit 1
fi

if [ -z "$PACKAGE_NAME" ]; then
    echo "Error: Could not extract package name from pyproject.toml"
    exit 1
fi

echo "Package Information:"
echo "  Name: $PACKAGE_NAME"
echo "  Version: $PACKAGE_VERSION"
echo ""

# Ask for user confirmation
read -p "Do you want to proceed with building and publishing version $PACKAGE_VERSION? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Build cancelled by user."
    exit 0
fi

echo "Proceeding with build..."
echo ""

# Check if build tools are available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "build_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv build_env
fi

# Activate virtual environment and install build tools
echo "Installing build tools..."
source build_env/bin/activate
pip install --upgrade pip
pip install build twine

# Build the package
echo "Building package..."
python -m build

# Check the package
echo "Checking package..."
twine check dist/*

echo ""
echo "=== Package built successfully! ==="
echo ""
echo "Package files created:"
ls -la dist/
echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Test the package locally (optional):"
echo "   pip install dist/$PACKAGE_NAME-$PACKAGE_VERSION-py3-none-any.whl"
echo ""
echo "2. Upload to Test PyPI (recommended first):"
echo "   twine upload --repository testpypi dist/*"
echo ""
echo "3. Upload to PyPI (production):"
echo "   twine upload dist/*"
echo ""
echo "Note: You'll need PyPI credentials for uploading."
echo "For Test PyPI: https://test.pypi.org/account/register/"
echo "For PyPI: https://pypi.org/account/register/"
echo ""
echo "=== Package Information ==="
echo "Name: $PACKAGE_NAME"
echo "Version: $PACKAGE_VERSION"
echo "Description: A specialized translation tool for SNOMED CT terminology translation and management, based on Weblate"
echo ""
echo "After publishing, users can install with:"
echo "pip install $PACKAGE_NAME"
