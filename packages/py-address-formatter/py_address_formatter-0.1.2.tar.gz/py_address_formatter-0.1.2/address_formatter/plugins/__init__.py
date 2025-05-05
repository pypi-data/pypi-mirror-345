"""
Address Formatter Plugin System

This package provides the plugin system for the address formatter,
allowing extensibility without modifying core components.
"""

from address_formatter.plugins.manager import PluginManager

# Export the plugin manager
plugin_manager = PluginManager()

__all__ = ['plugin_manager'] 