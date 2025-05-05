"""
Command-line interface for the address formatter.

This module provides a command-line interface for the address formatter,
allowing for formatting addresses, running the API server, and managing
templates from the command line.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, List, Optional, Union
import csv
import asyncio

from .formatter import format_address, AddressFormatter
from .async_api import format_batch_async
from .api.server import run_server
from .config import settings
from .monitoring.metrics import MetricsCollector
from . import __version__

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Address formatter command-line interface",
        prog="address-formatter"
    )
    
    # Add version argument
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Format command
    format_parser = subparsers.add_parser(
        "format",
        help="Format an address"
    )
    format_parser.add_argument(
        "--input",
        "-i",
        help="Input file containing address components (JSON)",
        type=str
    )
    format_parser.add_argument(
        "--abbreviate",
        "-a",
        help="Abbreviate address components",
        action="store_true"
    )
    format_parser.add_argument(
        "--append-country",
        "-c",
        help="Append country to formatted address",
        action="store_true"
    )
    format_parser.add_argument(
        "--output",
        "-o",
        help="Output file for formatted address",
        type=str
    )
    
    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Format multiple addresses"
    )
    batch_parser.add_argument(
        "--input",
        "-i",
        help="Input file containing multiple addresses (JSON or CSV)",
        type=str,
        required=True
    )
    batch_parser.add_argument(
        "--abbreviate",
        "-a",
        help="Abbreviate address components",
        action="store_true"
    )
    batch_parser.add_argument(
        "--append-country",
        "-c",
        help="Append country to formatted address",
        action="store_true"
    )
    batch_parser.add_argument(
        "--output",
        "-o",
        help="Output file for formatted addresses",
        type=str,
        required=True
    )
    batch_parser.add_argument(
        "--format",
        "-f",
        help="Input/output format (json or csv)",
        choices=["json", "csv"],
        default="json"
    )
    
    # Server command
    server_parser = subparsers.add_parser(
        "server",
        help="Run the API server"
    )
    server_parser.add_argument(
        "--host",
        help=f"Host to bind to (default: {settings.api.host})",
        default=settings.api.host
    )
    server_parser.add_argument(
        "--port",
        "-p",
        help=f"Port to bind to (default: {settings.api.port})",
        type=int,
        default=settings.api.port
    )
    server_parser.add_argument(
        "--reload",
        "-r",
        help="Enable auto-reload",
        action="store_true"
    )
    
    # Stats command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show formatter statistics"
    )
    
    return parser.parse_args()

def read_address_json(file_path: str) -> Dict[str, Any]:
    """
    Read address components from a JSON file.
    
    Args:
        file_path: Path to the JSON file.
        
    Returns:
        Address components dictionary.
    """
    with open(file_path, "r") as f:
        return json.load(f)

def read_addresses_csv(file_path: str) -> List[Dict[str, str]]:
    """
    Read multiple addresses from a CSV file.
    
    Args:
        file_path: Path to the CSV file.
        
    Returns:
        List of address component dictionaries.
    """
    addresses = []
    
    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            addresses.append({k.strip(): v.strip() for k, v in row.items() if v.strip()})
    
    return addresses

def read_addresses_json(file_path: str) -> List[Dict[str, str]]:
    """
    Read multiple addresses from a JSON file.
    
    Args:
        file_path: Path to the JSON file.
        
    Returns:
        List of address component dictionaries.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
        
        # Handle both list and object formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "addresses" in data:
            return data["addresses"]
        else:
            return [data]  # Single address

def write_formatted_json(formatted: Union[str, List[str]], file_path: str) -> None:
    """
    Write formatted address to a JSON file.
    
    Args:
        formatted: Formatted address.
        file_path: Path to the output file.
    """
    with open(file_path, "w") as f:
        json.dump({"formatted": formatted}, f, indent=2)

def write_batch_json(results: List[Union[str, List[str]]], file_path: str) -> None:
    """
    Write batch results to a JSON file.
    
    Args:
        results: List of formatted addresses.
        file_path: Path to the output file.
    """
    with open(file_path, "w") as f:
        json.dump({"results": results}, f, indent=2)

def write_batch_csv(results: List[Union[str, List[str]]], file_path: str) -> None:
    """
    Write batch results to a CSV file.
    
    Args:
        results: List of formatted addresses.
        file_path: Path to the output file.
    """
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["formatted_address"])
        
        for result in results:
            if isinstance(result, list):
                writer.writerow(["\n".join(result)])
            else:
                writer.writerow([result])

async def process_batch(addresses: List[Dict[str, str]], options: Dict[str, Any]) -> List[Union[str, List[str]]]:
    """
    Process a batch of addresses asynchronously.
    
    Args:
        addresses: List of address components.
        options: Formatting options.
        
    Returns:
        List of formatted addresses.
    """
    return await format_batch_async(addresses, options)

def show_stats() -> None:
    """Show formatter statistics."""
    formatter = AddressFormatter()
    stats = MetricsCollector.collect_formatter_metrics(formatter)
    
    print(f"Address Formatter v{__version__}")
    print("-" * 40)
    print(f"Cache size: {stats['cache']['size']}")
    print(f"Templates: {stats['templates']['count']}")
    print(f"Plugins: {stats['plugins']['count']}")

def main() -> None:
    """Run the CLI."""
    args = parse_args()
    
    if args.command == "format":
        # Format a single address
        options = {
            "abbreviate": args.abbreviate,
            "append_country": args.append_country
        }
        
        if args.input:
            components = read_address_json(args.input)
        else:
            # Read from stdin
            components = json.load(sys.stdin)
        
        formatted = format_address(components, options)
        
        if args.output:
            write_formatted_json(formatted, args.output)
        else:
            # Write to stdout
            if isinstance(formatted, list):
                print("\n".join(formatted))
            else:
                print(formatted)
    
    elif args.command == "batch":
        # Format multiple addresses
        options = {
            "abbreviate": args.abbreviate,
            "append_country": args.append_country
        }
        
        # Read addresses
        if args.format == "json":
            addresses = read_addresses_json(args.input)
        else:
            addresses = read_addresses_csv(args.input)
        
        # Process batch
        if settings.enable_async:
            # Run asynchronously
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(process_batch(addresses, options))
        else:
            # Run synchronously
            results = [format_address(addr, options) for addr in addresses]
        
        # Write results
        if args.format == "json":
            write_batch_json(results, args.output)
        else:
            write_batch_csv(results, args.output)
    
    elif args.command == "server":
        # Run the API server
        run_server(args.host, args.port, args.reload)
    
    elif args.command == "stats":
        # Show formatter statistics
        show_stats()
    
    else:
        # No command specified, show help
        parse_args(["--help"])

if __name__ == "__main__":
    main() 