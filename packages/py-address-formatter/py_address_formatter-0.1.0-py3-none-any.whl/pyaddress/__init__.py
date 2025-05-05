"""
PyAddress - A comprehensive address formatting library

PyAddress formats address components according to country-specific rules using
templates from the OpenCageData address-formatting repository.
"""

__version__ = "0.1.0"

# Re-export main functionality
from address_formatter.formatter import format_address, AddressFormatter

# For backward compatibility with the new package name
import sys
sys.modules['py_address_formatter'] = sys.modules[__name__]

__all__ = ["format_address", "AddressFormatter", "__version__"]