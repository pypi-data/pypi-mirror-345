"""
Address Formatter Package

This package provides functionality for formatting address components
according to country-specific templates and standards.
"""

from typing import Dict, Any, Optional

# Import core components
from address_formatter.core.formatter import AddressFormatter

__all__ = ['AddressFormatter', 'format_address']

def format_address(address_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> str:
    """
    Format address components according to country-specific standards.
    
    This is the main function for formatting addresses. It instantiates a formatter
    and uses it to format the address components.
    
    Args:
        address_data: Dictionary containing address components
        options: Optional formatting options
        
    Returns:
        Formatted address string
        
    Examples:
        >>> format_address({
        ...     'house_number': '123',
        ...     'road': 'Main St',
        ...     'city': 'Anytown', 
        ...     'country_code': 'US'
        ... })
        '123 Main St\nAnytown\nUnited States of America'
    """
    formatter = AddressFormatter()
    
    # Get the country code from the address data if available
    country_code = None
    if 'country_code' in address_data:
        country_code = address_data['country_code']
    
    return formatter.format(address_data, country_code, options or {}) 