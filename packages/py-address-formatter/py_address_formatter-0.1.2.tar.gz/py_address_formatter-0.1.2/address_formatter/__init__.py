"""
Address Formatter Package

This package provides functionality for formatting address components
according to country-specific templates and standards.
"""

from typing import Dict, Any, Optional

# Import core components
from address_formatter.core.formatter import AddressFormatter

__version__ = "0.1.2"  # Match version with the package

__all__ = ['AddressFormatter', 'format_address', '__version__']

def format_address(address_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> str:
    """
    Format address components according to country-specific standards.

    This is the main function for formatting addresses. It instantiates a formatter
    and uses it to format the address components.

    Args:
        address_data: Dictionary containing address components. Common keys include:
            - house_number: The house or building number
            - road: The street or road name
            - city: The city or town
            - state: The state, province, or region
            - postcode: The postal or ZIP code
            - country_code: The ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB')
            - name: The name of a person or business associated with the address
            - suburb: A suburb or neighborhood
            - district: A district or county
            - building: A building name or number

        options: Optional formatting options. Available options include:
            - abbreviate (bool): Whether to abbreviate address components (default: False)
            - add_country (bool): Whether to include the country name (default: True)
            - output_format (str): Output format, one of 'string' or 'array' (default: 'string')
            - country_name_format (str): Format for country names, one of 'full', 'iso', or 'short' (default: 'full')
            - uppercase (list): List of components to convert to uppercase
            - lowercase (list): List of components to convert to lowercase
            - capitalize (list): List of components to capitalize
            - language (str): Language code for localization (e.g., 'en', 'fr')

    Returns:
        Formatted address string or list of address lines if output_format is 'array'

    Examples:
        >>> format_address({
        ...     'house_number': '123',
        ...     'road': 'Main St',
        ...     'city': 'Anytown',
        ...     'country_code': 'US'
        ... })
        '123 Main St\nAnytown\nUnited States of America'

        >>> format_address({
        ...     'house_number': '123',
        ...     'road': 'Main St',
        ...     'city': 'Anytown',
        ...     'state': 'California',
        ...     'country_code': 'US'
        ... }, options={'abbreviate': True, 'add_country': False})
        '123 Main St\nAnytown, CA'

        >>> format_address({
        ...     'house_number': '123',
        ...     'road': 'Main St',
        ...     'city': 'Anytown',
        ...     'country_code': 'US'
        ... }, options={'output_format': 'array'})
        ['123 Main St', 'Anytown', 'United States of America']
    """
    formatter = AddressFormatter()

    # Get the country code from the address data if available
    country_code = None
    if 'country_code' in address_data:
        country_code = address_data['country_code']

    return formatter.format(address_data, country_code, options or {})