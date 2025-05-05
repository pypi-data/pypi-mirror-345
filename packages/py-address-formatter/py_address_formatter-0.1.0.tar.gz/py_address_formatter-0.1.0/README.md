# Python Address Formatter

A comprehensive Python library for formatting addresses according to country-specific templates and rules. Built on the OpenCageData address-formatting templates, this library provides robust support for international address formatting.

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
pip install pyaddress
```

### Installation with Extra Features

```bash
# Install with API support
pip install pyaddress[api]

# Install with async support
pip install pyaddress[async]

# Install with ML support
pip install pyaddress[ml]

# Install with optimization support
pip install pyaddress[optimize]

# Install with all features
pip install pyaddress[api,async,ml,optimize]
```

## Quick Start

### Format an Address

```python
from address_formatter import format_address

# Format an address
formatted = format_address({
    "houseNumber": "123",
    "road": "Main St",
    "city": "Anytown",
    "state": "CA",
    "countryCode": "US",
    "postcode": "12345"
})

print(formatted)
# Output: 123 Main St
#         Anytown CA 12345
```

### Format with Options

```python
# Format with options
formatted = format_address({
    "houseNumber": "123",
    "road": "Main Street",
    "city": "Anytown",
    "state": "California",
    "countryCode": "US",
    "postcode": "12345"
}, {
    "abbreviate": True,
    "append_country": True,
    "output": "array"
})

print(formatted)
# Output: ['123 Main St', 'Anytown CA 12345', 'United States']
```

### Async Processing

```python
import asyncio
from address_formatter import format_address_async, format_batch_async

async def main():
    # Format a single address asynchronously
    formatted = await format_address_async({
        "houseNumber": "123",
        "road": "Main St",
        "city": "Anytown",
        "state": "CA",
        "countryCode": "US"
    })
    print(formatted)
    
    # Process a batch of addresses asynchronously
    addresses = [
        {
            "houseNumber": "123",
            "road": "Main St",
            "city": "Anytown",
            "state": "CA",
            "countryCode": "US"
        },
        {
            "houseNumber": "456",
            "road": "High St",
            "city": "Othertown",
            "state": "NY",
            "countryCode": "US"
        }
    ]
    results = await format_batch_async(addresses)
    print(results)

asyncio.run(main())
```

## Command-Line Interface

The library includes a command-line interface for easy access to formatting functionality:

```bash
# Format a single address
address-formatter format --input address.json --abbreviate

# Process a batch of addresses
address-formatter batch --input addresses.csv --output formatted.csv --format csv

# Run the API server
address-formatter server --port 8000

# Show formatter statistics
address-formatter stats
```

## API Server

Start the API server with:

```bash
# Using the CLI
address-formatter server

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
docker build -t address-formatter .

# Run the container
docker run -p 8000:8000 address-formatter
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCageData for the address-formatting templates
- All contributors to the project 