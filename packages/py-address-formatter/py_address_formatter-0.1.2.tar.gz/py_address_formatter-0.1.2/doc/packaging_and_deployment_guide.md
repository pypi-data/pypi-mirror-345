# PyAddress: Packaging, Deployment and Integration Guide

This document provides comprehensive instructions for packaging, deploying, and integrating the PyAddress library into other projects.

## Table of Contents

1. [Packaging Process](#packaging-process)
2. [Deployment Process](#deployment-process)
3. [Using PyAddress in Another Project](#using-pyaddress-in-another-project)
4. [Private GitHub Package Integration](#private-github-package-integration)
5. [External GitHub Project Integration](#external-github-project-integration)
6. [Common Use Cases](#common-use-cases)

## Packaging Process

The PyAddress library is structured as a Python package that can be distributed via PyPI or as a private GitHub package. Below are the steps to package the library for distribution:

### Prerequisites

- Python 3.8 or higher
- pip
- setuptools
- twine (for PyPI distribution)
- wheel
- git

### Building the Package

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/pyaddress.git
   cd pyaddress
   ```

2. **Configure package metadata**:
   Ensure that `setup.py` contains the correct package metadata, including dependencies:
   ```python
   setup(
       name="pyaddress",
       version="0.1.0",
       description="Python library for formatting addresses according to country-specific rules",
       # Other metadata...
       packages=[
           'pyaddress',
           'address_formatter',
           'address_formatter.core',
           # Other packages...
       ],
       # Dependencies...
   )
   ```

3. **Run the build command**:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install --upgrade build
   python -m build
   ```
   
   This will create both source distributions (`.tar.gz`) and wheel distributions (`.whl`) in the `dist/` directory.

4. **Run tests to verify packaging**:
   ```bash
   python -m pip install -e .
   python -m pytest tests/
   ```

### Creating a GitHub Release

1. **Tag the release**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

2. **Create a release on GitHub**:
   - Go to the repository on GitHub
   - Navigate to "Releases"
   - Click "Create a new release"
   - Select the tag you just pushed
   - Add release notes
   - Attach the distribution files from the `dist/` directory

## Deployment Process

### Deploying to PyPI

1. **Register on PyPI** if you haven't already:
   - Create an account at https://pypi.org/account/register/
   - Verify your email

2. **Prepare credentials**:
   - Create a `~/.pypirc` file:
     ```
     [distutils]
     index-servers =
         pypi
         testpypi

     [pypi]
     username = your_username
     password = your_password

     [testpypi]
     repository = https://test.pypi.org/legacy/
     username = your_username
     password = your_password
     ```

3. **Upload to Test PyPI** (recommended first step):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

4. **Test the installation**:
   ```bash
   python -m pip install --index-url https://test.pypi.org/simple/ pyaddress
   ```

5. **Upload to Production PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

### Publishing as a GitHub Package

1. **Configure GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `read:packages` and `write:packages` scopes

2. **Configure credentials**:
   ```bash
   pip config set global.index-url https://pypi.org/simple/
   pip config set global.extra-index-url https://USERNAME:TOKEN@github.com/yourusername/pyaddress/
   ```

3. **Create GitHub workflow file** (`.github/workflows/publish.yml`):
   ```yaml
   name: Build and publish Python package

   on:
     release:
       types: [created]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: '3.x'
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install build twine
       - name: Build and publish
         env:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         run: |
           python -m build
           python -m twine upload --repository-url https://github.com/yourusername/pyaddress/ dist/*
   ```

4. **Push to GitHub and create a release** to trigger the workflow.

## Using PyAddress in Another Project

### Installation

#### From PyPI

```bash
pip install pyaddress
```

#### From GitHub (Public Repository)

```bash
pip install git+https://github.com/yourusername/pyaddress.git
```

#### From GitHub (Private Repository)

```bash
pip install git+https://${GITHUB_TOKEN}@github.com/yourusername/pyaddress.git
```

Where `${GITHUB_TOKEN}` is your GitHub Personal Access Token.

### Basic Usage

Here's how to use PyAddress in your Python project:

```python
from pyaddress import format_address

# Format a simple address
address = {
    'street': '123 Main St',
    'city': 'Anytown',
    'state': 'CA',
    'country_code': 'US'
}

formatted_address = format_address(address)
print(formatted_address)
# Output:
# 123 Main St
# Anytown, CA
# United States of America
```

### Advanced Usage with AddressFormatter

For more control, you can directly use the `AddressFormatter` class:

```python
from pyaddress import AddressFormatter

# Create a formatter instance
formatter = AddressFormatter()

# Format an address with custom options
address = {
    'street': '123 Main St',
    'city': 'Anytown',
    'state': 'CA',
    'country_code': 'US'
}

options = {
    'abbreviate': True,
    'add_country': False
}

formatted_address = formatter.format(address, options=options)
print(formatted_address)
# Output:
# 123 Main St
# Anytown, CA
```

### Batch Processing

For processing multiple addresses:

```python
from pyaddress import AddressFormatter

# Create a formatter instance
formatter = AddressFormatter()

# List of addresses
addresses = [
    {
        'street': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'country_code': 'US'
    },
    {
        'street': '456 Elm St',
        'city': 'Othertown',
        'state': 'NY',
        'country_code': 'US'
    }
]

# Process each address
for address in addresses:
    print(formatter.format(address))
    print("---")
```

## Private GitHub Package Integration

To use PyAddress as a private GitHub package, follow these steps:

### Setting Up Authentication

1. **Create a GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `read:packages` scope
   - Copy the token

2. **Configure pip to use the token**:

   Create or modify `~/.pip/pip.conf` (Linux/Mac) or `%APPDATA%\pip\pip.ini` (Windows):
   ```
   [global]
   extra-index-url = https://USERNAME:TOKEN@github.com/yourusername/pyaddress/
   ```

   Alternatively, set up environment variables or configure at the project level:
   ```bash
   export PIP_EXTRA_INDEX_URL=https://USERNAME:TOKEN@github.com/yourusername/pyaddress/
   ```

### Dependency Management

1. **In requirements.txt**:
   ```
   pyaddress @ git+https://USERNAME:TOKEN@github.com/yourusername/pyaddress.git@v0.1.0
   ```

2. **In setup.py**:
   ```python
   setup(
       # ...
       dependency_links=[
           'git+https://USERNAME:TOKEN@github.com/yourusername/pyaddress.git@v0.1.0#egg=pyaddress-0.1.0',
       ],
       install_requires=[
           'pyaddress==0.1.0',
           # Other dependencies...
       ],
   )
   ```

3. **In Poetry projects** (`pyproject.toml`):
   ```toml
   [tool.poetry.dependencies]
   pyaddress = { git = "https://github.com/yourusername/pyaddress.git", tag = "v0.1.0" }
   ```

### CI/CD Integration

For GitHub Actions workflows that need to access private packages:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - name: Install dependencies
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          pip config set global.extra-index-url https://USERNAME:${GITHUB_TOKEN}@github.com/yourusername/pyaddress/
          pip install -r requirements.txt
```

## External GitHub Project Integration

PyAddress utilizes the OpenCageData address-formatting GitHub repository for reference data and templates. Here's how it fits into the overall solution:

### Address-Formatting Repository

The [address-formatting](https://github.com/OpenCageData/address-formatting) repository contains:

1. **Country-specific templates**: Used for formatting addresses according to local conventions
2. **Test fixtures**: Used to verify correct formatting
3. **Component mappings**: Used to handle different naming conventions

### Integration Process

1. **Template Loading**:
   - PyAddress includes a subset of templates from the address-formatting repository
   - The `TemplateLoader` class loads these templates at runtime

2. **Template Management**:
   ```python
   from address_formatter.core.template_loader import TemplateLoader
   
   loader = TemplateLoader()
   template = loader.get_template('US')
   print(template)
   ```

3. **Updating Templates**:
   - To update templates from the repository:
   ```bash
   python -m address_formatter.management.process_templates
   ```

This script fetches the latest templates from the OpenCageData repository and integrates them with PyAddress.

### Custom Template Usage

You can provide your own templates if needed:

```python
from pyaddress import AddressFormatter

# Create a formatter with custom template path
formatter = AddressFormatter(template_path='/path/to/custom_templates.json')

# Format an address using custom templates
address = {...}
formatted = formatter.format(address)
```

## Common Use Cases

### Web Service Integration

```python
from fastapi import FastAPI
from pydantic import BaseModel
from pyaddress import format_address

app = FastAPI()

class AddressInput(BaseModel):
    street: str
    city: str
    state: str = None
    postal_code: str = None
    country_code: str

@app.post("/format-address/")
def format_address_endpoint(address: AddressInput):
    formatted = format_address(address.dict())
    return {"formatted_address": formatted}
```

### Database Address Normalization

```python
import sqlite3
from pyaddress import AddressFormatter

# Connect to database
conn = sqlite3.connect('customer_database.db')
cursor = conn.cursor()

# Get addresses
cursor.execute("SELECT id, street, city, state, postal_code, country_code FROM addresses")
addresses = cursor.fetchall()

# Format addresses
formatter = AddressFormatter()
for id, street, city, state, postal_code, country_code in addresses:
    address = {
        'street': street,
        'city': city,
        'state': state,
        'postal_code': postal_code,
        'country_code': country_code
    }
    
    formatted = formatter.format(address)
    
    # Update database
    cursor.execute(
        "UPDATE addresses SET formatted_address = ? WHERE id = ?",
        (formatted, id)
    )

conn.commit()
conn.close()
```

### Command-Line Tool

```python
import argparse
import json
from pyaddress import format_address

def main():
    parser = argparse.ArgumentParser(description='Format an address')
    parser.add_argument('--street', required=True, help='Street address')
    parser.add_argument('--city', required=True, help='City')
    parser.add_argument('--state', help='State or province')
    parser.add_argument('--postal-code', help='Postal or ZIP code')
    parser.add_argument('--country-code', required=True, help='Country code')
    
    args = parser.parse_args()
    
    address = {
        'street': args.street,
        'city': args.city,
        'state': args.state,
        'postal_code': args.postal_code,
        'country_code': args.country_code
    }
    
    formatted = format_address(address)
    print(formatted)

if __name__ == '__main__':
    main()
```

---

This guide covers the essential steps for packaging, deploying, and integrating the PyAddress library. For more detailed examples or specific use cases, refer to the other documentation files or open an issue on the GitHub repository. 

..................................................


The name "pyaddress" in the documentation is actually a placeholder name that I used for illustrative purposes. It isn't necessarily the actual or final name of your project.

In the examples throughout the documentation, I used this placeholder based on:

1. The directory structure I observed in your project (which shows a main directory called "pyaddress")
2. The common Python convention of prefixing library names with "py" to indicate they're Python packages (like "pymongo", "pytest", "pytz", etc.)

This is a common practice in documentation to provide generic examples that users can later substitute with their actual project name.

If you have a different preferred name for your package, you should replace all instances of "pyaddress" in:

1. The GitHub repository URL (`github.com/yourusername/pyaddress.git`)
2. The package name in setup.py (`name="pyaddress"`)
3. The import statements (`from pyaddress import format_address`)
4. The installation commands (`pip install pyaddress`)

The name choice impacts:

1. **Discoverability**: The name affects how easily users can find your package
2. **Memorability**: A descriptive name helps users remember your package
3. **Namespace conflicts**: Ensuring your name doesn't conflict with existing PyPI packages
4. **Branding**: Building recognition around your package name

If you'd like to rename the package from "pyaddress" to something else, you should update the documentation accordingly. Common naming patterns for address formatting libraries might include names like:

- addressformat
- address-formatter
- formattedaddress
- addformatpy
- formataddress

Would you like me to update the documentation with a different name for the package?
...............................................


The two `pyaddress` folders serve different purposes in the project structure, following a common pattern in Python packaging:

### 1. Root `pyaddress/` folder
This is the **project root directory** that contains everything related to the project:
- All source code
- Documentation
- Configuration files
- Tests
- Build scripts
- etc.

This is the main container for the entire project and is typically the repository root. It's where you'd run build commands, tests, and other project-wide operations.

### 2. Inner `pyaddress/pyaddress/` folder
This is the **actual Python package** that gets installed when users install your library:
- Contains the `__init__.py` file defining the importable package
- This is what becomes available when users do `import pyaddress`
- Typically contains the core functionality or re-exports from other subpackages

### Relevance in Python Packaging

This nested structure follows a common Python packaging pattern called the "src layout" or "package layout" (though your implementation is a slight variation):

1. The outer directory is the project container
2. The inner directory with the same name is the actual importable package

### Specific Benefits

1. **Import clarity**: Having an inner `pyaddress` package prevents confusion between project-level imports and package-level imports
   
2. **Development isolation**: It ensures that when running tests, you're testing the package as it would be installed, not as it exists in your development environment

3. **Installation correctness**: The structure ensures that when the package is installed, only the inner `pyaddress` directory (and other specified packages like `address_formatter`) are installed, not development files like tests or documentation

### In Your Project

Your structure is interesting because you have:
- The outer `/pyaddress/` (project root)
- The inner `/pyaddress/pyaddress/` (the main package)
- A separate `/pyaddress/address_formatter/` (a subpackage)

This suggests your architecture has:
1. A main package (`pyaddress`) that acts as an entry point and public API
2. A subpackage (`address_formatter`) that contains the actual implementation
3. The main package likely imports and re-exports functionality from the subpackage

This separation creates a clean public API while keeping implementation details in a different namespace.
