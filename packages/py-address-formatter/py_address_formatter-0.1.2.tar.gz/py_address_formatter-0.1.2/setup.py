from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README.md
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

# Read version from __init__.py
import re
init_path = Path(__file__).parent / "pyaddress" / "__init__.py"
if init_path.exists():
    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", init_path.read_text())
    version = version_match.group(1) if version_match else "0.1.0"
else:
    version = "0.1.0"

# Package setup
setup(
    name="py-address-formatter",
    version=version,
    description="Python library for formatting addresses according to country-specific rules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Solchos",
    author_email="solchos@gmail.com",
    url="https://github.com/address-formatter/pyaddress",
    # Specify packages explicitly
    packages=[
        'pyaddress',
        'address_formatter',
        'address_formatter.core',
        'address_formatter.management',
        'address_formatter.plugins',
        'address_formatter.plugins.builtins',
        'address_formatter.api',
        'address_formatter.events',
        'address_formatter.cache',
        'address_formatter.monitoring',
        'address_formatter.data',
        'ml',
    ],
    include_package_data=True,
    package_data={
        "address_formatter": ["data/templates/*.json", "data/templates/*.yaml", "data/templates/*.yml"],
    },
    install_requires=[
        "pyyaml>=6.0",
        "chevron>=0.14.0",
        "python-slugify>=8.0.0",
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
        "pydantic-settings>=2.0.0",
        "uvicorn>=0.15.0",
        "prometheus-client>=0.13.0",
        "click>=8.1.0",
    ],
    extras_require={
        "api": [
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
            "prometheus-client>=0.13.0",
        ],
        "async": [
            "aiofiles>=0.8.0",
            "asyncio>=3.4.3",
            "httpx>=0.22.0",
        ],
        "ml": [
            "spacy>=3.4.0",
            "sentence-transformers>=2.2.0",
            "networkx>=2.8.0",
        ],
        "optimize": [
            "numba>=0.56.0; platform_machine != 'arm64'",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "mypy>=0.910",
            "hypothesis>=6.0.0",
            "black>=21.5b2",
            "isort>=5.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "py-address-formatter=address_formatter.cli:main",
            "address-formatter=address_formatter.compat:main",  # For backward compatibility
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    zip_safe=False,
)