# Snowlate Package Building and Publishing

This document explains how to build and publish the Snowlate package for distribution via pip.

## Overview

Snowlate is a specialized translation tool for SNOMED CT terminology translation and management, based on the open source Weblate project. The package is configured to be installable via pip.

## Package Information

- **Name**: `snowlate`
- **Description**: A specialized translation tool for SNOMED CT terminology translation and management, based on Weblate
- **License**: GPL-3.0-or-later
- **Python Version**: >=3.11

## Quick Start

### Using the Automated Script

The easiest way to build and prepare the package for publishing is to use the provided script:

```bash
./publish_package.sh
```

This script will:
1. Create a virtual environment
2. Install build tools
3. Build the package
4. Validate the package
5. Show next steps for publishing

### Manual Build Process

If you prefer to build manually:

1. **Create a virtual environment**:
   ```bash
   python3 -m venv build_env
   source build_env/bin/activate
   ```

2. **Install build tools**:
   ```bash
   pip install build twine
   ```

3. **Build the package**:
   ```bash
   python -m build
   ```

4. **Check the package**:
   ```bash
   twine check dist/*
   ```

## Package Contents

The built package includes:
- All Weblate source code
- Static files (CSS, JS, images)
- Templates
- Documentation
- Configuration files
- Dependencies (specified in pyproject.toml)

## Publishing to PyPI

### Test PyPI (Recommended First)

Before publishing to the main PyPI, test on Test PyPI:

1. **Register on Test PyPI**: https://test.pypi.org/account/register/
2. **Upload to Test PyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```
3. **Test installation**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ snowlate
   ```

### Production PyPI

Once tested, publish to the main PyPI:

1. **Register on PyPI**: https://pypi.org/account/register/
2. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## Installation

After publishing, users can install Snowlate with:

```bash
pip install snowlate
```

## Dependencies

Snowlate has many dependencies including:
- Django and related packages
- Translation tools (translate-toolkit)
- Database drivers
- Image processing libraries
- And many more (see pyproject.toml for complete list)

## System Requirements

Note that Snowlate requires several system-level dependencies that are not included in the Python package:
- Database server (PostgreSQL, MySQL, etc.)
- Redis (for caching and Celery)
- Git
- Various system libraries for image processing, OCR, etc.

See the main Weblate documentation for complete installation requirements.

## Version Management

To update the package version:

1. Update the version in `pyproject.toml`
2. Update the version in `weblate/__init__.py`
3. Rebuild the package
4. Publish the new version

## Troubleshooting

### Build Issues

If you encounter build issues:
- Ensure you have Python 3.11+ installed
- Check that all build dependencies are available
- Verify the virtual environment is activated

### Installation Issues

The package itself installs fine, but running Snowlate requires:
- Proper system dependencies
- Database setup
- Configuration
- Web server setup

See the Weblate documentation for complete setup instructions.

## License

Snowlate is licensed under the GNU General Public License v3.0 or later, same as Weblate.
