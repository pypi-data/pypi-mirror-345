"""
Built-in plugins for the address formatter.

This package provides a set of built-in plugins for the address formatter.
"""

from address_formatter.plugins.builtins.abbreviation_plugin import AbbreviationPlugin
from address_formatter.plugins.builtins.add_country_plugin import AddCountryPlugin
from address_formatter.plugins.builtins.output_format_plugin import OutputFormatPlugin
from address_formatter.plugins.builtins.ml_integration_plugin import MLIntegrationPlugin

# Export the plugins
__all__ = [
    'AbbreviationPlugin',
    'AddCountryPlugin',
    'OutputFormatPlugin',
    'MLIntegrationPlugin',
]

# Instantiate plugins for auto-registration
abbreviation_plugin = AbbreviationPlugin()
add_country_plugin = AddCountryPlugin()
output_format_plugin = OutputFormatPlugin()
ml_integration_plugin = MLIntegrationPlugin() 