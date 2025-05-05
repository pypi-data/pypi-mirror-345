# Python Address Formatter

A comprehensive Python library for formatting addresses according to country-specific templates and rules. Built on the OpenCageData address-formatting templates, this library provides robust support for international address formatting.

[![PyPI version](https://badge.fury.io/py/py-address-formatter.svg)](https://badge.fury.io/py/py-address-formatter)
[![Python Versions](https://img.shields.io/pypi/pyversions/py-address-formatter.svg)](https://pypi.org/project/py-address-formatter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Country-Specific Formatting**: Format addresses according to country-specific rules and templates
- **Component Normalization**: Normalize address components with alias support and key conversion
- **Abbreviation Support**: Apply language-specific abbreviations to address components
- **Template Management**: Automatic conversion of YAML templates to JSON for runtime efficiency
- **Plugin System**: Extensible architecture with plugin support
- **Event System**: Event-driven architecture for flexible processing
- **Machine Learning Integration**: Component prediction and extraction from unstructured text
- **API Support**: FastAPI-based REST API for address formatting
- **Monitoring**: Prometheus metrics for monitoring performance and errors
- **Asynchronous Processing**: Support for async/await and batch processing
- **CLI Tool**: Command-line interface for formatter access
- **Type System**: Comprehensive type hints and Pydantic models

## Installation

### Basic Installation

```bash
pip install py-address-formatter
```

### Installation with Extra Features

```bash
# Install with API support
pip install py-address-formatter[api]

# Install with async support
pip install py-address-formatter[async]

# Install with ML support
pip install py-address-formatter[ml]

# Install with optimization support
pip install py-address-formatter[optimize]

# Install with all features
pip install py-address-formatter[api,async,ml,optimize]

# Install development dependencies
pip install py-address-formatter[dev]
```

## Quick Start

### Format an Address

```python
from pyaddress import format_address

# Format an address
formatted = format_address({
    "house_number": "123",
    "road": "Main St",
    "city": "Anytown",
    "state": "CA",
    "country_code": "US",
    "postcode": "12345"
})

print(formatted)
# Output: 123 Main St
#         Anytown, California 12345
#         United States of America
```

### Format with Options

```python
# Format with options
formatted = format_address({
    "house_number": "123",
    "road": "Main Street",
    "city": "Anytown",
    "state": "California",
    "country_code": "US",
    "postcode": "12345"
}, options={
    "abbreviate": True,
    "add_country": False,
    "output_format": "array"
})

print(formatted)
# Output: 123 Main St
#         Anytown, CA 12345
```

### International Addresses

```python
# Format a UK address
uk_address = format_address({
    "house_number": "10",
    "road": "Downing Street",
    "city": "London",
    "postcode": "SW1A 2AA",
    "country_code": "GB"
})

print(uk_address)
# Output: 10 Downing Street
#         London
#         SW1A 2AA
#         United Kingdom

# Format a German address
de_address = format_address({
    "house_number": "1",
    "road": "Platz der Republik",
    "city": "Berlin",
    "postcode": "11011",
    "country_code": "DE"
})

print(de_address)
# Output: Platz der Republik 1
#         11011 Berlin
#         Germany
```

### Async Processing

```python
import asyncio
from pyaddress import format_address_async, format_batch_async

async def main():
    # Format a single address asynchronously
    formatted = await format_address_async({
        "house_number": "123",
        "road": "Main St",
        "city": "Anytown",
        "state": "CA",
        "country_code": "US"
    })
    print(formatted)

    # Process a batch of addresses asynchronously
    addresses = [
        {
            "house_number": "123",
            "road": "Main St",
            "city": "Anytown",
            "state": "CA",
            "country_code": "US"
        },
        {
            "house_number": "456",
            "road": "High St",
            "city": "Othertown",
            "state": "NY",
            "country_code": "US"
        }
    ]
    results = await format_batch_async(addresses)
    print(results)

asyncio.run(main())
```

### Special Cases

```python
# Address with a name
named_address = format_address({
    "name": "John Doe",
    "house_number": "123",
    "road": "Main St",
    "city": "Anytown",
    "state": "CA",
    "country_code": "US"
})

print(named_address)
# Output: John Doe
#         123 Main St
#         Anytown, California
#         United States of America

# PO Box
po_box = format_address({
    "po_box": "PO Box 1234",
    "city": "Anytown",
    "state": "CA",
    "postcode": "12345",
    "country_code": "US"
})

print(po_box)
# Output: PO Box 1234
#         Anytown, California 12345
#         United States of America
```

## Command-Line Interface

The library includes a command-line interface for easy access to formatting functionality:

```bash
# Format a single address
py-address-formatter format --input address.json --abbreviate

# Process a batch of addresses
py-address-formatter batch --input addresses.csv --output formatted.csv --format csv

# Run the API server
py-address-formatter server --port 8000

# Show formatter statistics
py-address-formatter stats

# Show help
py-address-formatter --help
```

### CLI Options

```
Usage: py-address-formatter [OPTIONS] COMMAND [ARGS]...

  Address Formatter CLI tool.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  batch    Format a batch of addresses from a file.
  format   Format a single address.
  server   Run the API server.
  stats    Show formatter statistics.
```

## API Server

Start the API server with:

```bash
# Using the CLI
py-address-formatter server

# Or directly with Python
python -m address_formatter.api.server
```

Once running, you can access the API at `http://localhost:8000` and view the API documentation at `http://localhost:8000/docs`.

### API Endpoints

- **POST /format**: Format a single address
- **POST /batch**: Format multiple addresses
- **POST /validate**: Validate address components
- **GET /health**: Check API health
- **GET /metrics**: Get Prometheus metrics
- **GET /stats**: Get formatter statistics

### API Examples

#### Format a Single Address

```bash
curl -X POST "http://localhost:8000/format" \
  -H "Content-Type: application/json" \
  -d '{
    "address": {
      "house_number": "123",
      "road": "Main St",
      "city": "Anytown",
      "state": "CA",
      "country_code": "US"
    },
    "options": {
      "abbreviate": true,
      "add_country": true
    }
  }'
```

Response:
```json
{
  "formatted": "123 Main St\nAnytown, CA\nUnited States of America"
}
```

#### Format Multiple Addresses

```bash
curl -X POST "http://localhost:8000/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      {
        "house_number": "123",
        "road": "Main St",
        "city": "Anytown",
        "state": "CA",
        "country_code": "US"
      },
      {
        "house_number": "10",
        "road": "Downing Street",
        "city": "London",
        "country_code": "GB"
      }
    ],
    "options": {
      "abbreviate": true
    }
  }'
```

Response:
```json
{
  "results": [
    {
      "formatted": "123 Main St\nAnytown, CA\nUnited States of America"
    },
    {
      "formatted": "10 Downing St\nLondon\nUnited Kingdom"
    }
  ]
}
```

## Configuration

The formatter can be configured through environment variables:

```bash
# Address formatter configuration
export ADDRESS_TEMPLATE_DIR=/path/to/templates
export CACHE_SIZE=1000
export DEFAULT_LANG=en

# API configuration
export API_HOST=0.0.0.0
export API_PORT=8000
export API_RATE_LIMIT=100

# Performance configuration
export ENABLE_ASYNC=true
export ENABLE_JIT=false
export THREAD_POOL_SIZE=4
```

## Docker Support

You can run the address formatter in a Docker container:

```bash
# Build the Docker image
docker build -t py-address-formatter .

# Run the container
docker run -p 8000:8000 py-address-formatter

# Run with custom configuration
docker run -p 8000:8000 \
  -e ADDRESS_TEMPLATE_DIR=/app/templates \
  -e API_PORT=8000 \
  -e ENABLE_ASYNC=true \
  py-address-formatter
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository with submodules
git clone --recurse-submodules https://github.com/address-formatter/pyaddress.git

# Navigate to the project directory
cd pyaddress

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Building and Publishing

See the [Building and Publishing the Package](https://github.com/address-formatter/pyaddress#building-and-publishing-the-package) section for detailed instructions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenCageData](https://opencagedata.com) for the address-formatting templates
- All contributors to the project

## Changelog

### 0.1.1 (2025-05-04)
- Fixed CLI issue with missing `__version__` variable
- Improved documentation with more examples
- Added comprehensive tests for edge cases
- Updated README with better examples and API documentation

### 0.1.0 (2025-05-04)
- Initial release
- Support for 250+ countries and territories
- Command-line interface
- API server
- Async processing support