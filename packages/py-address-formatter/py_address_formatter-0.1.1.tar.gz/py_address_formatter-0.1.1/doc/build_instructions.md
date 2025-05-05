# PyAddress: Comprehensive Build Instructions

This document provides detailed, step-by-step instructions for building the PyAddress package from source code.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Package Structure Verification](#package-structure-verification)
4. [Building the Package](#building-the-package)
5. [Testing the Built Package](#testing-the-built-package)
6. [Troubleshooting Common Issues](#troubleshooting-common-issues)
7. [Additional Build Options](#additional-build-options)

## Prerequisites

Before starting the build process, ensure you have the following installed:

- **Python 3.8 or higher**: Required for the build process
  ```bash
  python --version  # Should show 3.8.x or higher
  ```

- **pip**: Package installer for Python
  ```bash
  pip --version  # Should be up-to-date
  ```

- **Git**: Version control system
  ```bash
  git --version  # Should be installed
  ```

- **Required build tools**: Essential packages for building Python distributions
  ```bash
  python -m pip install --upgrade pip setuptools wheel build twine
  ```

## Environment Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/yourusername/pyaddress.git
   cd pyaddress
   ```

2. **Create and activate a virtual environment**:

   **Windows**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

   **macOS/Linux**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Package Structure Verification

Before building, verify the package structure is correct:

1. **Check directory structure**:
   ```bash
   # Should include these key directories
   ls -la
   ```
   
   Ensure you have these key directories:
   - `pyaddress/` - Main package directory
   - `address_formatter/` - Core formatter code
   - `tests/` - Test files
   - `data/` - Template data

2. **Verify setup.py file**:
   ```bash
   cat setup.py
   ```
   
   Ensure it contains:
   - Correct package name and version
   - All dependencies listed
   - Proper package structure defined

3. **Check package imports**:
   ```bash
   # Ensure imports are properly structured
   grep -r "import" pyaddress/ address_formatter/ | grep -v "__pycache__"
   ```
   
   Make sure imports use the correct structure (e.g., `from address_formatter.core.normalizer import AddressNormalizer`)

## Building the Package

Now that everything is verified, follow these steps to build the package:

1. **Clean any previous builds**:
   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

2. **Update version number** (if needed):
   Edit the version in `pyaddress/__init__.py`:
   ```python
   __version__ = "0.1.0"  # Update this value
   ```

3. **Run the build command**:
   ```bash
   python -m build
   ```
   
   This will create:
   - A source distribution (`.tar.gz`) in `dist/`
   - A wheel distribution (`.whl`) in `dist/`

4. **Verify the build artifacts**:
   ```bash
   ls -la dist/
   ```
   
   You should see files like:
   - `pyaddress-0.1.0.tar.gz` (source distribution)
   - `pyaddress-0.1.0-py3-none-any.whl` (wheel distribution)

## Testing the Built Package

Before distributing, test the built package:

1. **Create a clean test environment**:
   ```bash
   mkdir -p ~/test-pyaddress
   cd ~/test-pyaddress
   python -m venv test-env
   ```

2. **Activate the test environment**:

   **Windows**:
   ```bash
   test-env\Scripts\activate.bat
   ```
   
   **macOS/Linux**:
   ```bash
   source test-env/bin/activate
   ```

3. **Install the built package**:
   ```bash
   pip install /path/to/pyaddress/dist/pyaddress-0.1.0-py3-none-any.whl
   ```

4. **Verify the installation**:
   ```bash
   python -c "import pyaddress; print(pyaddress.__version__)"
   ```
   
   Should output: `0.1.0` (or your current version)

5. **Run a basic functionality test**:
   ```bash
   python -c "from pyaddress import format_address; print(format_address({'street': '123 Main St', 'city': 'Anytown', 'country_code': 'US'}))"
   ```
   
   Should output a formatted US address.

## Troubleshooting Common Issues

### Issue 1: Import Errors During Build

If you encounter import errors during build:

1. **Check for circular imports**:
   ```bash
   grep -r "from pyaddress" address_formatter/
   grep -r "from address_formatter" pyaddress/
   ```

2. **Fix by updating imports** to use the correct structure:
   ```python
   # Change this:
   from pyaddress.address_formatter.core import normalizer
   
   # To this:
   from address_formatter.core import normalizer
   ```

### Issue 2: Missing Dependencies

If the build fails due to missing dependencies:

1. **Check for any missing requirements**:
   ```bash
   pip install -e .
   ```
   
   This will show if any required packages are missing.

2. **Update setup.py** with the missing dependencies:
   ```python
   setup(
       # ...
       install_requires=[
           'existing_dependency>=1.0.0',
           'missing_dependency>=2.0.0',  # Add the missing dependency
       ],
   )
   ```

### Issue 3: File Not Found Errors

If you get "file not found" errors during build:

1. **Check MANIFEST.in** to ensure all necessary files are included:
   ```bash
   cat MANIFEST.in
   ```

2. **Update MANIFEST.in** if needed:
   ```
   include README.md
   include LICENSE
   recursive-include pyaddress/data *.json
   recursive-include address_formatter/data *.json
   ```

## Additional Build Options

### Building a Development Installation

For development work, install in editable mode:

```bash
pip install -e .
```

### Building with Custom Options

Control which extras are included:

```bash
python -m build --wheel  # Build only the wheel
python -m build --sdist  # Build only the source distribution
```

### Building for Different Python Versions

The standard build creates a universal wheel, but you can specify Python versions:

1. **Update setup.py** with Python classifiers:
   ```python
   setup(
       # ...
       classifiers=[
           'Programming Language :: Python :: 3.8',
           'Programming Language :: Python :: 3.9',
           'Programming Language :: Python :: 3.10',
       ],
       python_requires='>=3.8',
   )
   ```

2. **Run the build** as usual:
   ```bash
   python -m build
   ```

### Automating the Build Process

Create a build script (`build.sh` or `build.bat`) for automation:

**build.sh (Linux/macOS)**:
```bash
#!/bin/bash
set -e  # Exit on error

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Update version if provided
if [ ! -z "$1" ]; then
    sed -i "s/__version__ = \".*\"/__version__ = \"$1\"/" pyaddress/__init__.py
    echo "Updated version to $1"
fi

# Run tests
python -m pytest tests/

# Build package
python -m build

echo "Build completed successfully!"
ls -la dist/
```

**build.bat (Windows)**:
```batch
@echo off
REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info

REM Run tests
python -m pytest tests\

REM Build package
python -m build

echo Build completed successfully!
dir dist\
```

Make the script executable:
```bash
chmod +x build.sh  # For Linux/macOS
```

## Next Steps

After successfully building the package, you can:

1. **Upload to PyPI**: Instructions in [Packaging and Deployment Guide](packaging_and_deployment_guide.md)
2. **Create a GitHub Release**: Package the build artifacts with a tagged release
3. **Install locally**: Use the built wheel for local installation

For more details on deployment options, refer to the comprehensive [Packaging and Deployment Guide](packaging_and_deployment_guide.md).

---

This guide provides the complete step-by-step process for building the PyAddress package. If you encounter specific issues not covered here, please consult the Python Packaging User Guide or open an issue in the project repository. 