# Local Installation and Docker Deployment Guide

This guide provides detailed steps for installing the PyAddress package locally on a Windows machine and deploying it in a Docker environment.

## Table of Contents

1. [Local Installation](#local-installation)
   - [Development Mode Installation](#development-mode-installation)
   - [Standard Package Installation](#standard-package-installation)
   - [Direct Local Reference](#direct-local-reference)
   - [Testing the Local Installation](#testing-the-local-installation)
   - [Troubleshooting Local Installation](#troubleshooting-local-installation)

2. [Docker Deployment](#docker-deployment)
   - [Using PyAddress as a Dependency in an Existing Docker Project](#using-pyaddress-as-a-dependency-in-an-existing-docker-project)
   - [Using the Existing Dockerfile](#using-the-existing-dockerfile)
   - [Creating a Custom Dockerfile](#creating-a-custom-dockerfile)
   - [Building the Docker Image](#building-the-docker-image)
   - [Running the Container](#running-the-container)
   - [Docker Compose Setup](#docker-compose-setup)
   - [Multi-stage Docker Builds](#multi-stage-docker-builds)

3. [CI/CD Integration](#cicd-integration)
   - [Automating Docker Builds](#automating-docker-builds)
   - [Integration with GitHub Actions](#integration-with-github-actions)

4. [Git Submodules](#git-submodules)
   - [Understanding the Address-Formatting Submodule](#understanding-the-address-formatting-submodule)
   - [Working with Submodules in Your Project](#working-with-submodules-in-your-project)

5. [Using PyAddress from a Private Repository](#using-pyaddress-from-a-private-repository)
   - [Authentication for Private Repositories](#authentication-for-private-repositories)
   - [Installing from a Private Repository](#installing-from-a-private-repository)
   - [Docker with Private Repositories](#docker-with-private-repositories)
   - [CI/CD with Private Repositories](#cicd-with-private-repositories)
   - [Troubleshooting Private Repository Access](#troubleshooting-private-repository-access)

## Local Installation

When both your project and the PyAddress package are on the same machine, you have several options for installation.

### Development Mode Installation

This method is recommended during development as it creates a symbolic link to your source code, allowing changes to be immediately reflected without reinstallation.

#### Step 1: Navigate to the project directory

```bash
cd C:\Projects\Address\pyaddress
```

#### Step 2: Activate your virtual environment (if using one)

```bash
.venv\Scripts\activate.bat
```

#### Step 3: Install in development mode

```bash
pip install -e .
```

**What this does:**
- Creates a reference to your project in site-packages
- Any code changes are immediately available without reinstallation
- Package metadata (including entry points) is properly registered

### Standard Package Installation

For testing the actual installable package:

#### Step 1: Build the package

```bash
cd C:\Projects\Address\pyaddress
python -m pip install --upgrade build
python -m build
```

This creates:
- A source distribution (.tar.gz) in the dist/ directory
- A wheel (.whl) in the dist/ directory

#### Step 2: Install the wheel

```bash
pip install dist\pyaddress-0.1.0-py3-none-any.whl
```

**Note:** Replace the version number with your actual package version.

### Direct Local Reference

If you need to reference PyAddress from another local project:

#### Step 1: Add a direct reference in your other project's requirements.txt

```
-e C:/Projects/Address/pyaddress
```

#### Step 2: Install the requirements

```bash
pip install -r requirements.txt
```

### Testing the Local Installation

Verify the installation with a simple test:

#### Method 1: Command-line test

```bash
python -c "from pyaddress import format_address; print(format_address({'street': '123 Main St', 'city': 'Anytown', 'country_code': 'US'}))"
```

#### Method 2: Run the demo script

```bash
python nigeria_demo.py
```

### Troubleshooting Local Installation

If you encounter issues:

1. **Import errors**:
   - Check that the package structure matches what's declared in setup.py
   - Ensure imports use the correct paths
   - Try `pip list` to confirm the package is installed

2. **Version conflicts**:
   - Uninstall any existing versions: `pip uninstall pyaddress`
   - Check for conflicts with other packages

3. **Installation fails**:
   - Check for syntax errors in setup.py
   - Ensure all required files are included in MANIFEST.in
   - Try with `--verbose` flag: `pip install -e . --verbose`

## Docker Deployment

Docker provides a consistent environment for deploying PyAddress, regardless of the host system.

### Using PyAddress as a Dependency in an Existing Docker Project

If you want to use PyAddress as a package in an existing Python Docker image, you have several options depending on your project setup and requirements.

#### Option 1: Install from PyPI or GitHub Packages

If PyAddress is published to PyPI or GitHub Packages, you can include it in your project's requirements.txt file:

```
# requirements.txt
pyaddress==0.1.0
```

Then in your Dockerfile, install the requirements as usual:

```dockerfile
# In your existing Dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
```

#### Option 2: Include as a Wheel in Your Project

If you want to bundle PyAddress with your project:

1. Build the wheel file locally:
```bash
cd C:\Projects\Address\pyaddress
python -m build
```

2. Copy the resulting .whl file to your project:
```bash
cp pyaddress/dist/pyaddress-0.1.0-py3-none-any.whl your-project/vendor/
```

3. Update your Dockerfile to install the wheel:
```dockerfile
# In your existing Dockerfile
COPY vendor/pyaddress-0.1.0-py3-none-any.whl /tmp/
RUN pip install /tmp/pyaddress-0.1.0-py3-none-any.whl
```

#### Option 3: Install Directly from Git

Add PyAddress to your requirements.txt file as a git dependency:

```
# requirements.txt
git+https://github.com/yourusername/pyaddress.git@main
```

Then in your Dockerfile:

```dockerfile
# Make sure git is installed
RUN apt-get update && apt-get install -y git

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
```

#### Option 4: Mount as a Volume for Development

For development purposes, you can mount the PyAddress directory as a volume and install it in development mode:

```yaml
# docker-compose.yml
version: '3'
services:
  your-app:
    build: .
    volumes:
      - /path/to/pyaddress:/pyaddress
    command: >
      sh -c "pip install -e /pyaddress && python your_application.py"
```

#### Using PyAddress in Your Application Container

Once installed, you can use PyAddress in your application code:

```python
# In your application code
from pyaddress import format_address

address = {
    'street': '123 Main St', 
    'city': 'Anytown', 
    'country_code': 'US'
}

formatted_address = format_address(address)
print(formatted_address)
```

#### Template Customization in Docker

To use custom templates with PyAddress in a Docker container:

1. Create a directory for custom templates in your project:
```
your-project/
  ├── custom_templates/
  │   ├── US.json
  │   └── NG.json
  └── ...
```

2. Mount this directory in your Docker Compose file:
```yaml
services:
  your-app:
    # ... other config ...
    volumes:
      - ./custom_templates:/app/custom_templates
    environment:
      - ADDRESS_FORMATTER_TEMPLATE_PATH=/app/custom_templates
```

3. In your code, initialize the formatter with the custom template path:
```python
from pyaddress import AddressFormatter

formatter = AddressFormatter(template_path="/app/custom_templates")
```

### Using the Existing Dockerfile

The PyAddress project already includes a Dockerfile:

#### Step 1: Review the existing Dockerfile

```bash
cat Dockerfile
```

#### Step 2: Build the Docker image

```bash
docker build -t pyaddress:latest .
```

#### Step 3: Run a container from the image

```bash
docker run -it --rm pyaddress:latest python -c "from pyaddress import format_address; print(format_address({'street': '123 Main St', 'city': 'Anytown', 'country_code': 'US'}))"
```

### Creating a Custom Dockerfile

If you need a custom Docker configuration:

#### Step 1: Create a new Dockerfile

```dockerfile
# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# For a local installation, use either:
# Option 1: Copy the entire project and install
COPY . .
RUN pip install .

# Option 2: If you've built a wheel
# COPY dist/pyaddress-0.1.0-py3-none-any.whl .
# RUN pip install pyaddress-0.1.0-py3-none-any.whl

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run when container starts
CMD ["python", "-c", "from pyaddress import format_address; print('PyAddress is installed!')"]
```

#### Step 2: Build the custom image

```bash
docker build -t pyaddress-custom:latest -f Dockerfile.custom .
```

### Building the Docker Image

For more advanced Docker builds:

#### Step 1: Build with build arguments

```bash
docker build -t pyaddress:latest --build-arg PYTHON_VERSION=3.9 .
```

#### Step 2: Build for multiple platforms

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t pyaddress:multi-arch --push .
```

### Running the Container

Different ways to run the PyAddress container:

#### Basic run

```bash
docker run -it --rm pyaddress:latest
```

#### Run with mounted volume for persistent data

```bash
docker run -it --rm -v C:/data:/app/data pyaddress:latest
```

#### Run in detached mode as a service

```bash
docker run -d --name pyaddress-service -p 8000:8000 pyaddress:latest
```

### Docker Compose Setup

For more complex deployments, use Docker Compose:

#### Step 1: Create a docker-compose.yml file

```yaml
version: '3'

services:
  pyaddress:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - "8000:8000"
    command: python -m address_formatter.api.server

  # Add additional services as needed
  database:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=addresses
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Step 2: Start the services

```bash
docker-compose up -d
```

### Multi-stage Docker Builds

For optimized production images:

```dockerfile
# Build stage
FROM python:3.9 AS builder

WORKDIR /build
COPY . .

# Install build tools and dependencies
RUN pip install --no-cache-dir build wheel
RUN python -m build

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Copy wheel from builder stage
COPY --from=builder /build/dist/*.whl /app/

# Install package without keeping build dependencies
RUN pip install --no-cache-dir *.whl && rm *.whl

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -m appuser
USER appuser

# Command to run when container starts
CMD ["python", "-m", "address_formatter.api.server"]
```

## CI/CD Integration

### Automating Docker Builds

#### GitHub Actions workflow for Docker builds

Create a `.github/workflows/docker-build.yml` file:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1

      - name: Login to DockerHub
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v3
        with:
          images: yourusername/pyaddress
          tags: |
            type=semver,pattern={{version}}
            type=ref,event=branch
            type=sha,format=short

      - name: Build and push
        uses: docker/build-push-action@v2
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=yourusername/pyaddress:buildcache
          cache-to: type=registry,ref=yourusername/pyaddress:buildcache,mode=max
```

### Integration with GitHub Actions

For more comprehensive CI/CD pipelines, integrate testing, building, and deployment:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
          pip install -e .
      - name: Test with pytest
        run: |
          pytest

  build-and-push:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Python package
        run: |
          python -m pip install --upgrade pip build
          python -m build
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: yourusername/pyaddress:latest
```

## Git Submodules

PyAddress uses Git submodules to include external dependencies like the OpenCageData `address-formatting` repository.

### Understanding the Address-Formatting Submodule

The PyAddress project uses the `address-formatting` submodule defined in the `.gitmodules` file:

```
[submodule "address-formatting"]
    path = pyaddress/address-formatting
    url = https://github.com/OpenCageData/address-formatting.git
```

This submodule contains critical templates and formatting rules that PyAddress depends on.

#### How Submodules Are Pulled

When cloning a repository that contains submodules, you need to be aware of the following:

1. **Standard Git Clone**: By default, when you clone the PyAddress repository, the submodule directories will be created but **no content will be pulled**:

```bash
git clone https://github.com/yourusername/pyaddress.git
```

After this command, the `pyaddress/address-formatting` directory will exist but be empty.

2. **Clone with Submodules**: To clone the repository and automatically initialize and update all submodules:

```bash
git clone --recurse-submodules https://github.com/yourusername/pyaddress.git
```

3. **Pull Submodules After Cloning**: If you've already cloned the repository without the `--recurse-submodules` flag:

```bash
cd pyaddress
git submodule init
git submodule update
```

### Working with Submodules in Your Project

When using PyAddress as a dependency in another project, you have several options:

#### Option 1: Installing from PyPI (Recommended)

When the package is installed from PyPI, the submodule content is already included in the package, so no extra steps are required.

#### Option 2: Installing Directly from Git

When installing directly from Git, you need to ensure submodules are included:

```
# requirements.txt
git+https://github.com/yourusername/pyaddress.git@main#egg=pyaddress
```

In your Dockerfile, you need to use the `--recurse-submodules` flag:

```dockerfile
# Install git
RUN apt-get update && apt-get install -y git

# Clone with submodules and install
RUN git clone --recurse-submodules https://github.com/yourusername/pyaddress.git /tmp/pyaddress \
    && pip install /tmp/pyaddress \
    && rm -rf /tmp/pyaddress
```

Alternatively, use pip's Git support with the `subdirectory` option:

```dockerfile
# Install git
RUN apt-get update && apt-get install -y git

# Install directly from Git with submodules
RUN pip install git+https://github.com/yourusername/pyaddress.git@main#egg=pyaddress
```

By default, pip will attempt to initialize and update submodules when installing from a Git repository.

#### Option 3: Docker Multi-stage Build with Submodules

For Docker, use a multi-stage build to ensure submodules are correctly included:

```dockerfile
# Clone stage
FROM alpine/git as clone
WORKDIR /app
RUN git clone --recurse-submodules https://github.com/yourusername/pyaddress.git .

# Build stage
FROM python:3.9 as builder
WORKDIR /app
COPY --from=clone /app /app
RUN pip install build && python -m build

# Final stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /app/dist/*.whl /app/
RUN pip install *.whl && rm *.whl
```

#### Note on CI/CD Pipelines

In CI/CD pipelines, make sure to include the `--recurse-submodules` flag or equivalent configuration:

```yaml
# GitHub Actions example
- name: Checkout code with submodules
  uses: actions/checkout@v2
  with:
    submodules: recursive
```

### Submodules and .gitignore

Even if the `address-formatting` directory is listed in `.gitignore`, the submodule reference in `.gitmodules` ensures that Git still tracks the submodule. The `.gitignore` entry might be there to prevent accidentally committing the submodule content directly, as Git submodules are meant to reference a specific commit in the external repository.

This approach maintains the separation between PyAddress code and the external address-formatting templates while ensuring they're available when needed.

## Specific Docker Environment Considerations

### Python Version Compatibility
Ensure your Dockerfile uses a Python version compatible with PyAddress:

```dockerfile
FROM python:3.8-slim  # Minimum recommended version
```

### Environment Variables

Configure the package behavior with environment variables:

```dockerfile
ENV ADDRESS_FORMATTER_TEMPLATE_PATH=/app/custom_templates
ENV ADDRESS_FORMATTER_LOG_LEVEL=INFO
```

### Volume Mounting

For template customization, mount volumes:

```bash
docker run -v /path/to/templates:/app/templates pyaddress:latest
```

### Container Health Checks

Add health checks to your Dockerfile for production use:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "from pyaddress import AddressFormatter; formatter = AddressFormatter(); formatter.get_supported_countries() or exit(1)"
```

## Using PyAddress from a Private Repository

When PyAddress is hosted in a private repository, you need to handle authentication differently. This section provides Windows-specific instructions for working with private repositories.

### Authentication for Private Repositories

#### Setting Up SSH Keys on Windows

1. Generate an SSH key if you don't have one:
   ```powershell
   # Open PowerShell and run
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

2. Add the key to your SSH agent:
   ```powershell
   # Start the SSH agent in PowerShell
   Get-Service ssh-agent | Set-Service -StartupType Automatic
   Start-Service ssh-agent
   
   # Add your key
   ssh-add $env:USERPROFILE\.ssh\id_rsa
   ```

3. Add the public key to your GitHub/GitLab account:
   - Copy the content of `%USERPROFILE%\.ssh\id_rsa.pub`
   - Add it to your Git provider's SSH keys section in account settings

4. Test your connection:
   ```powershell
   ssh -T git@github.com
   ```

#### Using Personal Access Tokens on Windows

1. Generate a Personal Access Token (PAT) from your Git provider:
   - GitHub: Profile → Settings → Developer settings → Personal access tokens
   - GitLab: Profile → Preferences → Access Tokens

2. Store the token securely:
   ```powershell
   # Set as environment variable in PowerShell
   $env:GH_TOKEN = "your_token_here"
   
   # To make it persistent (user level)
   [System.Environment]::SetEnvironmentVariable("GH_TOKEN", "your_token_here", "User")
   ```

### Installing from a Private Repository

#### Using SSH Authentication in requirements.txt

```
# requirements.txt
git+ssh://git@github.com/yourusername/pyaddress.git@main#egg=pyaddress
```

Install with:
```powershell
pip install -r requirements.txt
```

#### Using Personal Access Token Authentication

```
# requirements.txt (use environment variable syntax)
git+https://${GH_TOKEN}@github.com/yourusername/pyaddress.git@main#egg=pyaddress
```

Install with:
```powershell
# If token is stored as environment variable
pip install -r requirements.txt

# Or directly inline (not recommended for security)
$env:GH_TOKEN="your_token_here"; pip install -r requirements.txt
```

### Docker with Private Repositories

#### Using SSH Keys with Docker

1. Create a `.dockerignore` file to prevent adding sensitive files:
   ```
   .git
   .ssh
   **/.git
   **/.ssh
   ```

2. Create your Dockerfile:
   ```dockerfile
   FROM python:3.9
   
   # Install Git and SSH
   RUN apt-get update && apt-get install -y git openssh-client
   
   # Create SSH directory
   RUN mkdir -p /root/.ssh
   
   # Copy SSH key (this file will be added at build time)
   COPY id_rsa /root/.ssh/id_rsa
   RUN chmod 600 /root/.ssh/id_rsa
   
   # Add GitHub to known hosts
   RUN ssh-keyscan github.com >> /root/.ssh/known_hosts
   
   # Install your private package with submodules
   RUN pip install git+ssh://git@github.com/yourusername/pyaddress.git@main#egg=pyaddress
   
   # Your application setup
   WORKDIR /app
   COPY . .
   
   CMD ["python", "your_script.py"]
   ```

3. Prepare your SSH key for Docker build (create a temporary copy):
   ```powershell
   # PowerShell - temporarily copy your SSH key to the build context
   Copy-Item -Path "$env:USERPROFILE\.ssh\id_rsa" -Destination ".\id_rsa"
   ```

4. Build the Docker image:
   ```powershell
   docker build -t my-app-with-pyaddress .
   ```

5. Clean up the temporary SSH key:
   ```powershell
   # Clean up - IMPORTANT for security
   Remove-Item -Path ".\id_rsa"
   ```

#### Secure Multi-stage Build for Private Repositories

For better security, use a multi-stage build approach:

```dockerfile
# Build stage
FROM python:3.9 as builder

# Install Git and SSH
RUN apt-get update && apt-get install -y git openssh-client

# Create SSH directory
RUN mkdir -p /root/.ssh

# Copy SSH key
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts

# Install the package to a specific directory
RUN pip install --prefix=/install git+ssh://git@github.com/yourusername/pyaddress.git@main#egg=pyaddress

# Final stage - no credentials included
FROM python:3.9-slim

# Copy installed package from builder stage
COPY --from=builder /install /usr/local

# Your application setup
WORKDIR /app
COPY . .

CMD ["python", "your_script.py"]
```

Build with:
```powershell
# Temporarily copy your SSH key to the build context
Copy-Item -Path "$env:USERPROFILE\.ssh\id_rsa" -Destination ".\id_rsa"

# Build the image
docker build -t my-app-with-pyaddress-secure .

# Clean up
Remove-Item -Path ".\id_rsa"
```

#### Using Personal Access Tokens with Docker

Using a PAT with Docker is often simpler than SSH keys:

```dockerfile
FROM python:3.9

# Install Git
RUN apt-get update && apt-get install -y git

# Install from private repo using token
ARG GH_TOKEN
RUN pip install git+https://${GH_TOKEN}@github.com/yourusername/pyaddress.git@main#egg=pyaddress

# Your application setup
WORKDIR /app
COPY . .

CMD ["python", "your_script.py"]
```

Build with:
```powershell
docker build --build-arg GH_TOKEN="your_token_here" -t my-app-with-pyaddress .
```

### CI/CD with Private Repositories

#### GitHub Actions with Private Repository Access

```yaml
name: Build and Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
        run: |
          pip install git+https://${env:GH_TOKEN}@github.com/yourusername/pyaddress.git@main#egg=pyaddress
          pip install -r requirements.txt
```

#### Azure Pipelines with Private Repository Access

```yaml
trigger:
- main

pool:
  vmImage: 'windows-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'
    
- script: |
    pip install git+https://$(PAT)@github.com/yourusername/pyaddress.git@main#egg=pyaddress
    pip install -r requirements.txt
  env:
    PAT: $(PersonalAccessToken)
```

### Troubleshooting Private Repository Access

If you encounter issues when using private repositories:

1. **SSH Key Issues**:
   - Ensure your SSH key is properly loaded in the SSH agent: `ssh-add -l`
   - Check SSH connection: `ssh -T git@github.com`
   - Verify permissions on the key file (should be 600): `icacls %USERPROFILE%\.ssh\id_rsa`

2. **Personal Access Token Issues**:
   - Ensure your token has the correct scopes (repo, read:packages, etc.)
   - Check if the token is expired
   - Verify the token is correctly set as an environment variable

3. **Docker Issues**:
   - Use `docker build --no-cache` to prevent using cached layers with incorrect credentials
   - Check Docker logs: `docker logs container_name`
   - Try using `docker build --progress=plain` for more verbose output

4. **Pip Installation Issues**:
   - Run pip with verbose output: `pip install -v git+...`
   - Check Git credentials helper: `git config --list | findstr credential`
   - Verify that pip can access the Git repository: `git ls-remote git+ssh://git@github.com/yourusername/pyaddress.git`

This guide provides comprehensive instructions for both local installation on Windows and deployment in Docker environments. For additional details on package functionality, refer to the [Packaging and Deployment Guide](packaging_and_deployment_guide.md) and [Project Architecture](project_architecture.md) documentation. 